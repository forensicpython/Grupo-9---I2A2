#!/usr/bin/env python3
"""
Runner subprocess para executar CrewAI e capturar output real do terminal
"""

import sys
import os
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

class SubprocessCrewAIRunner:
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        
    async def run_instaprice(self, inputs):
        """
        Executa o Instaprice em subprocess e captura output real do terminal
        """
        try:
            # Cria script Python temporário para execução
            script_content = f'''#!/usr/bin/env python3
import sys
import os
import json

# Adiciona o diretório backend ao path
sys.path.insert(0, "{os.path.dirname(__file__)}")

from instaprice import Instaprice

def main():
    print("🚀 [SUBPROCESS] Iniciando execução do CrewAI...")
    
    # Inputs recebidos
    inputs = {repr(inputs)}
    
    print(f"📋 [SUBPROCESS] Configurações:")
    print(f"   • Arquivo ZIP: {{inputs['caminho_zip']}}")
    print(f"   • Pergunta: {{inputs['pergunta_usuario']}}")
    print(f"   • Diretório: {{inputs['diretorio_dados']}}")
    print("=" * 60)
    
    try:
        # Instancia e executa o Instaprice
        instaprice = Instaprice()
        resultado = instaprice.crew().kickoff(inputs=inputs)
        
        print("=" * 60)
        print("✅ [SUBPROCESS] Execução concluída!")
        print(f"📊 [SUBPROCESS] Resultado obtido: {{len(str(resultado))}} caracteres")
        
        # Lê apenas a resposta final do Porta-Voz do arquivo gerado
        porta_voz_file = "resposta_final_porta_voz.md"
        final_response = ""
        
        if os.path.exists(porta_voz_file):
            with open(porta_voz_file, "r", encoding="utf-8") as f:
                final_response = f.read().strip()
            print(f"📝 [SUBPROCESS] Resposta final capturada: {{len(final_response)}} caracteres")
        else:
            print("⚠️ [SUBPROCESS] Arquivo da resposta final não encontrado, usando resultado completo")
            final_response = str(resultado)
        
        # Retorna resultado como JSON na última linha
        print("__RESULT_START__")
        print(json.dumps({{"success": True, "result": final_response}}))
        print("__RESULT_END__")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ [SUBPROCESS] Erro durante execução: {{e}}")
        print("__RESULT_START__")
        print(json.dumps({{"success": False, "error": str(e)}}))
        print("__RESULT_END__")

if __name__ == "__main__":
    main()
'''
            
            # Salva script temporário
            script_path = "/tmp/instaprice_subprocess.py"
            with open(script_path, "w") as f:
                f.write(script_content)
            
            # Torna o script executável
            os.chmod(script_path, 0o755)
            
            # Executa o script e captura output em tempo real
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Captura output linha por linha em tempo real
            output_lines = []
            resultado_final = None
            capturing_result = False
            seen_lines = set()  # Cache para detectar duplicatas
            
            try:
                while True:
                    output = process.stdout.readline()
                    
                    # Se não há mais output e processo terminou
                    if output == '' and process.poll() is not None:
                        break
                        
                    if output:
                        line = output.rstrip('\n')
                        
                        # Detecta início/fim do resultado
                        if line == "__RESULT_START__":
                            capturing_result = True
                            continue
                        elif line == "__RESULT_END__":
                            capturing_result = False
                            continue
                        elif capturing_result:
                            try:
                                resultado_final = json.loads(line)
                            except:
                                pass
                            continue
                        
                        # Sistema inteligente de filtro de duplicação
                        skip_line = False
                        
                        # Remove prefixos e limpa a linha para comparação
                        clean_line = line.replace("[SUBPROCESS] ", "").strip()
                        
                        # Permite logs de progresso dos agentes (verbose)
                        is_agent_progress = any(marker in line for marker in [
                            "Agent", "Working Agent", "Task", "Tool", "Action:", "Observation:",
                            "Thought:", "🔄", "🚀", "✅", "❌", "⚠️", "📊", "🧠", "🎭", "💡", "🎩"
                        ])
                        
                        # Permite logs de sistema importantes
                        is_system_log = any(marker in line for marker in [
                            "[SUBPROCESS]", "Initiating", "Starting", "Completed", "Error", "Warning"
                        ])
                        
                        # Ignora linhas vazias ou apenas separadores
                        if not clean_line or clean_line == "=" * 60:
                            skip_line = True
                        
                        # Permite logs importantes sem verificar duplicação
                        elif is_agent_progress or is_system_log:
                            skip_line = False
                        
                        # Verifica duplicação apenas para conteúdo de resposta final
                        elif clean_line in seen_lines:
                            # Se é conteúdo longo (provável resposta de agente), bloqueia duplicação
                            if len(clean_line) > 50:
                                skip_line = True
                        
                        # Verifica duplicação de linhas consecutivas idênticas
                        elif output_lines and len(output_lines) > 0:
                            if output_lines[-1] == line:
                                skip_line = True
                        
                        if not skip_line:
                            # Adiciona linha limpa ao cache
                            seen_lines.add(clean_line)
                            
                            # Adiciona à lista de output
                            output_lines.append(line)
                            
                            # Envia para WebSocket em tempo real se disponível
                            if self.websocket_manager:
                                await self.websocket_manager.broadcast({
                                    "type": "agent_log",
                                    "data": {
                                        "message": output,  # Output exato com quebra de linha
                                        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                                        "raw_terminal": True
                                    }
                                })
                            
                            # Também imprime no console atual para debug
                            print(f"[SUBPROCESS] {line}")
                        
            except Exception as e:
                print(f"❌ Erro durante captura: {e}")
            
            # Aguarda conclusão do processo
            return_code = process.wait()
            
            # Remove script temporário
            try:
                os.remove(script_path)
            except:
                pass
            
            # Retorna resultado
            if resultado_final:
                return {
                    "success": resultado_final.get("success", False),
                    "result": resultado_final.get("result", ""),
                    "error": resultado_final.get("error", ""),
                    "output_lines": output_lines,
                    "return_code": return_code
                }
            else:
                return {
                    "success": False,
                    "error": f"Processo terminou com código {return_code}",
                    "output_lines": output_lines,
                    "return_code": return_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_lines": [],
                "return_code": -1
            }

# Função helper para uso direto
async def run_crewai_subprocess(inputs, websocket_manager=None):
    """Função helper para executar CrewAI via subprocess"""
    runner = SubprocessCrewAIRunner(websocket_manager)
    return await runner.run_instaprice(inputs)

if __name__ == "__main__":
    # Teste direto
    test_inputs = {
        'caminho_zip': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/202401_NFs.zip',
        'pergunta_usuario': 'Teste subprocess - mostre dados reais do terminal',
        'diretorio_dados': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/dados/notasfiscais'
    }
    
    async def test():
        result = await run_crewai_subprocess(test_inputs)
        print(f"✅ Resultado do teste: {result}")
    
    asyncio.run(test())