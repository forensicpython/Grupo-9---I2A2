#!/usr/bin/env python3
"""
Backend mínimo FastAPI para integração com frontend React
Integra com a lógica existente do Instaprice
"""

import os
import asyncio
import tempfile
import shutil
import sys
import io
import contextlib
import threading
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Importa a lógica existente do Instaprice
from instaprice import Instaprice
from utils.logger import setup_logger

# Configuração
app = FastAPI(title="Instaprice API", description="API para análise de notas fiscais", version="1.0.0")

# CORS para permitir frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = setup_logger()

# Handler de log customizado para WebSocket
class WebSocketLogHandler(logging.Handler):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
    def emit(self, record):
        if self.manager:
            try:
                # Cria uma task assíncrona para enviar via WebSocket
                loop = asyncio.get_event_loop()
                loop.create_task(self.manager.broadcast({
                    "type": "agent_log", 
                    "data": {
                        "message": self.format(record),
                        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "raw_terminal": True
                    }
                }))
            except Exception:
                pass

# Capturador de logs SEGURO - sem recursão
class SafeLogCapture:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.manager = None
        self.capturing = False
        
    def set_manager(self, manager):
        self.manager = manager
        
    def start_capture(self):
        """Substitui stdout por este objeto"""
        self.capturing = True
        sys.stdout = self
        
    def stop_capture(self):
        """Restaura stdout original"""
        self.capturing = False
        sys.stdout = self.original_stdout
        
    def write(self, text):
        """Método chamado quando algo é escrito no console"""
        # SEMPRE escreve no console original primeiro
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # Se estamos capturando e há um manager, tenta enviar
        if self.capturing and self.manager and text.strip():
            try:
                # Desabilita captura temporariamente para evitar recursão
                self.capturing = False
                
                # Envia via WebSocket de forma simples e segura
                import threading
                def send_in_thread():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.manager.broadcast({
                            "type": "agent_log",
                            "data": {
                                "message": text,
                                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                                "raw_terminal": True
                            }
                        }))
                        loop.close()
                    except:
                        pass
                
                thread = threading.Thread(target=send_in_thread, daemon=True)
                thread.start()
                
            except:
                pass
            finally:
                # Reabilita captura
                self.capturing = True
                
    def flush(self):
        """Implementa flush para compatibilidade"""
        self.original_stdout.flush()

# Gerenciamento de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nova conexão WebSocket estabelecida. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Conexão WebSocket encerrada. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast com tratamento robusto de erros"""
        dead_connections = []
        
        for connection in self.active_connections.copy():
            try:
                await asyncio.wait_for(
                    connection.send_json(message), 
                    timeout=5.0
                )
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning(f"Removendo conexão morta: {e}")
                dead_connections.append(connection)
        
        # Remove conexões mortas
        for dead_conn in dead_connections:
            try:
                self.active_connections.remove(dead_conn)
            except ValueError:
                pass  # Já foi removida

# Gerenciador de sessões de análise
class AnalysisSession:
    def __init__(self):
        self.sessions = {}  # {session_id: {file_id, dados_dir, extracted_data, instaprice_instance}}
    
    def create_session(self, file_id: str, dados_dir: str) -> str:
        """Cria nova sessão de análise"""
        session_id = f"session_{int(datetime.now().timestamp())}"
        self.sessions[session_id] = {
            'file_id': file_id,
            'dados_dir': dados_dir,
            'extracted_data': None,
            'instaprice_instance': None,
            'created_at': datetime.now(),
            'ready': False
        }
        return session_id
    
    def get_session(self, session_id: str):
        """Recupera sessão existente"""
        return self.sessions.get(session_id)
    
    def set_session_ready(self, session_id: str, instaprice_instance=None):
        """Marca sessão como pronta para consultas"""
        if session_id in self.sessions:
            self.sessions[session_id]['ready'] = True
            if instaprice_instance:
                self.sessions[session_id]['instaprice_instance'] = instaprice_instance
    
    def is_session_ready(self, session_id: str) -> bool:
        """Verifica se sessão está pronta"""
        session = self.sessions.get(session_id)
        return session and session.get('ready', False)

manager = ConnectionManager()
log_capture = SafeLogCapture()
log_capture.set_manager(manager)
analysis_sessions = AnalysisSession()

# Modelos Pydantic
class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    filename: Optional[str] = None

class ProcessResponse(BaseModel):
    success: bool
    message: str
    results: Optional[dict] = None
    suggestions_file: Optional[str] = None
    session_id: Optional[str] = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    message: str
    results: Optional[dict] = None

class ApiTestRequest(BaseModel):
    apiKey: str
    model: str

class ProcessRequest(BaseModel):
    apiKey: str
    model: str
    pergunta: str = "Analise os dados das notas fiscais"

# Diretório para uploads temporários
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Instaprice API está rodando!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload de arquivo para análise"""
    try:
        # Valida tipo de arquivo
        allowed_extensions = {'.zip', '.csv', '.xlsx', '.xls'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado: {file_extension}"
            )

        # Gera ID único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / file_id

        logger.info(f"UPLOAD_DIR: {UPLOAD_DIR.absolute()}")
        logger.info(f"file_path: {file_path.absolute()}")
        logger.info(f"file_path existe: {file_path.exists()}")

        # Salva arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Arquivo salvo: {file_path.absolute()} ({file.size} bytes)")

        # Envia notificação via WebSocket
        await manager.broadcast({
            "type": "file_uploaded",
            "data": {
                "file_id": file_id,
                "filename": file.filename,
                "size": file.size,
                "timestamp": datetime.now().isoformat()
            }
        })

        return UploadResponse(
            success=True,
            message="Arquivo enviado com sucesso!",
            file_id=file_id,
            filename=file.filename
        )

    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.post("/api/process/{file_id}", response_model=ProcessResponse)
async def process_file(file_id: str, request: ProcessRequest):
    """Processa arquivo com a lógica do Instaprice"""
    try:
        file_path = UPLOAD_DIR / file_id
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        # Envia notificação de início do processamento
        await manager.broadcast({
            "type": "processing_started",
            "data": {
                "file_id": file_id,
                "message": "Iniciando análise com robôs...",
                "timestamp": datetime.now().isoformat()
            }
        })

        # Usa o diretório de uploads como base (onde o tool extrairá)
        base_dir = UPLOAD_DIR
        dados_dir = base_dir / "dados" / "notasfiscais"
        dados_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processando arquivo: {file_path.absolute()}")
        logger.info(f"Base dir: {base_dir.absolute()}")
        logger.info(f"Diretório dados: {dados_dir.absolute()}")
        
        # Verifica se arquivo existe
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {file_path.absolute()}")

        # Cria sessão de análise
        session_id = analysis_sessions.create_session(file_id, str(dados_dir.absolute()))
        
        # Envia logs via WebSocket
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": f"🤖 Iniciando processamento de {file_id} (Sessão: {session_id})",
                "level": "info",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })

        # Instancia o Instaprice com configuração da API
        instaprice = Instaprice()
        
        # Configura a chave API dinamicamente
        import os
        os.environ["GROQ_API_KEY"] = request.apiKey
        
        # Prepara inputs para o CrewAI com caminhos absolutos
        inputs = {
            'caminho_zip': str(file_path.absolute()),
            'pergunta_usuario': request.pergunta,
            'diretorio_dados': str(dados_dir.absolute())
        }
        
        # NOVA ABORDAGEM: Executa CrewAI via subprocess para capturar terminal real
        try:
            from subprocess_runner import run_crewai_subprocess
            
            # Executa via subprocess e captura output real do terminal
            resultado_subprocess = await run_crewai_subprocess(inputs, manager)
            
            if resultado_subprocess["success"]:
                # Cria instância local do Instaprice para a sessão
                instaprice = Instaprice()
                analysis_sessions.set_session_ready(session_id, instaprice)
                resultado = resultado_subprocess["result"]
                
                await manager.broadcast({
                    "type": "log",
                    "data": {
                        "message": "✅ Subprocess executado com sucesso!",
                        "level": "success",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                })
            else:
                error_msg = resultado_subprocess.get("error", "Erro desconhecido no subprocess")
                raise Exception(f"Erro no subprocess: {error_msg}")
                
        except ImportError:
            # Fallback para método original se subprocess não disponível
            await manager.broadcast({
                "type": "log",
                "data": {
                    "message": "⚠️ Subprocess não disponível, usando método padrão...",
                    "level": "warning",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
            })
            
            log_capture.start_capture()
            try:
                resultado = instaprice.crew().kickoff(inputs=inputs)
                analysis_sessions.set_session_ready(session_id, instaprice)
            finally:
                log_capture.stop_capture()

        await manager.broadcast({
            "type": "log", 
            "data": {
                "message": "✅ Análise concluída com sucesso!",
                "level": "success",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })

        # Procura arquivo de sugestões
        suggestions_file = None
        for file in dados_dir.rglob("sugestoes_instaprice.md"):
            suggestions_file = str(file)
            break

        # Envia notificação de conclusão
        await manager.broadcast({
            "type": "processing_completed",
            "data": {
                "file_id": file_id,
                "message": "Análise concluída!",
                "timestamp": datetime.now().isoformat()
            }
        })

        return ProcessResponse(
            success=True,
            message="Arquivo processado com sucesso!",
            results={"resposta": resultado},
            suggestions_file=suggestions_file,
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": f"❌ Erro no processamento: {str(e)}",
                "level": "error", 
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })

        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.post("/api/query/{session_id}", response_model=QueryResponse)
async def query_session(session_id: str, request: QueryRequest):
    """Executa nova pergunta usando sessão existente sem reprocessar arquivo"""
    try:
        # Verifica se sessão existe e está pronta
        session = analysis_sessions.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        if not analysis_sessions.is_session_ready(session_id):
            raise HTTPException(status_code=400, detail="Sessão ainda não está pronta para consultas")
        
        # Recupera instância do Instaprice da sessão
        instaprice_instance = session.get('instaprice_instance')
        if not instaprice_instance:
            raise HTTPException(status_code=500, detail="Instância do Instaprice não encontrada na sessão")
        
        # Envia logs via WebSocket
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": f"🔍 Nova consulta na sessão {session_id}: {request.question}",
                "level": "info",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })
        
        # Prepara inputs apenas com pergunta (dados já processados)
        inputs = {
            'caminho_zip': session['file_id'],  # Mantém referência do arquivo original
            'pergunta_usuario': request.question,
            'diretorio_dados': session['dados_dir']
        }
        
        # Inicia captura de logs
        log_capture.start_capture()
        
        try:
            # Executa apenas a análise da nova pergunta
            resultado = instaprice_instance.crew().kickoff(inputs=inputs)
        finally:
            # Para captura de logs
            log_capture.stop_capture()
        
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": "✅ Nova consulta processada com sucesso!",
                "level": "success",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })
        
        return QueryResponse(
            success=True,
            message="Consulta processada com sucesso!",
            results={"resposta": resultado}
        )
        
    except Exception as e:
        logger.error(f"Erro na consulta da sessão: {str(e)}")
        
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": f"❌ Erro na consulta: {str(e)}",
                "level": "error",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        })
        
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")

@app.post("/api/groq/test")
async def test_groq_connection(request: ApiTestRequest):
    """Testa conexão com Groq API de forma rápida"""
    try:
        from crewai.llm import LLM
        
        # Configura LLM temporário apenas para teste de conexão
        test_llm = LLM(
            model=f"groq/{request.model}",
            api_key=request.apiKey,
            temperature=0.1,
            max_tokens=10  # Mínimo possível para ser rápido
        )
        
        # Faz uma chamada direta simples via LLM do CrewAI
        test_response = test_llm.call(
            messages=[{"role": "user", "content": "OK"}]
        )
        
        return {
            "success": True,
            "message": f"Conexão rápida bem-sucedida!",
            "model": request.model,
            "details": {
                "response": str(test_response)[:50] + "..." if len(str(test_response)) > 50 else str(test_response),
                "method": "CrewAI LLM Direct",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        error_message = str(e)
        
        # Tratamento específico para diferentes tipos de erro
        if "authentication" in error_message.lower() or "invalid" in error_message.lower() or "401" in error_message:
            return {
                "success": False,
                "message": "Chave API inválida ou expirada"
            }
        elif "not found" in error_message.lower() or "does not exist" in error_message.lower() or "404" in error_message:
            return {
                "success": False,
                "message": f"Modelo '{request.model}' não encontrado ou não disponível"
            }
        elif "rate limit" in error_message.lower() or "quota" in error_message.lower() or "429" in error_message:
            return {
                "success": False,
                "message": "Limite de taxa excedido. Tente novamente em alguns minutos"
            }
        else:
            return {
                "success": False,
                "message": f"Erro na conexão: {error_message}"
            }

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Download de arquivo processado"""
    file_path = UPLOAD_DIR / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=file_id,
        media_type='application/octet-stream'
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para logs em tempo real com heartbeat"""
    await manager.connect(websocket)
    try:
        # Enviar heartbeat a cada 30 segundos
        async def heartbeat():
            while websocket in manager.active_connections:
                try:
                    await websocket.ping()
                    await asyncio.sleep(30)
                except:
                    break
        
        heartbeat_task = asyncio.create_task(heartbeat())
        
        while True:
            try:
                # Aguarda mensagem com timeout
                message = await asyncio.wait_for(
                    websocket.receive_text(), 
                    timeout=60.0
                )
                # Echo da mensagem para manter viva
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            except asyncio.TimeoutError:
                # Timeout normal, continua loop
                continue
            except WebSocketDisconnect:
                break
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando servidor Instaprice...")
    print("📡 Frontend: http://localhost:5173")
    print("🔧 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=120,  # Keep-alive timeout
        timeout_graceful_shutdown=30,  # Graceful shutdown timeout
        limit_concurrency=100,  # Limit concurrent connections
        limit_max_requests=1000,  # Max requests per worker
        backlog=2048  # Socket backlog
    )