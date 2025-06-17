#!/usr/bin/env python3
"""
Teste completo do sistema com subprocess
"""

import asyncio
import websockets
import json
import aiohttp
import time

async def test_websocket():
    """Testa WebSocket para capturar logs em tempo real"""
    uri = "ws://localhost:8000/ws"
    
    print("📡 Conectando ao WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado ao WebSocket!")
            
            # Escuta mensagens por 5 minutos
            timeout = time.time() + 300  # 5 minutos
            
            while time.time() < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "agent_log" and data.get("data", {}).get("raw_terminal"):
                        print(f"🖥️  TERMINAL: {data['data']['message'].strip()}")
                    else:
                        print(f"📡 WebSocket: {data}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Erro WebSocket: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}")

async def test_api_call():
    """Faz chamada para API para iniciar processamento"""
    
    # Aguarda um pouco para estabelecer WebSocket
    await asyncio.sleep(2)
    
    print("🚀 Fazendo upload de arquivo...")
    
    try:
        # Upload de arquivo
        async with aiohttp.ClientSession() as session:
            with open('/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/202401_NFs.zip', 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='202401_NFs.zip')
                
                async with session.post('http://localhost:8000/api/upload', data=data) as resp:
                    upload_result = await resp.json()
                    print(f"📁 Upload result: {upload_result}")
                    
                    if upload_result.get('success'):
                        file_id = upload_result['file_id']
                        
                        print(f"🤖 Processando arquivo {file_id}...")
                        
                        # Processa arquivo
                        async with session.post(
                            f'http://localhost:8000/api/process/{file_id}',
                            params={'pergunta': 'Teste subprocess - mostre os dados reais das empresas'}
                        ) as resp:
                            process_result = await resp.json()
                            print(f"✅ Resultado do processamento: {process_result}")
                            
    except Exception as e:
        print(f"❌ Erro na API: {e}")

async def main():
    """Executa teste completo"""
    print("🧪 Iniciando teste completo do sistema...")
    
    # Executa WebSocket e API em paralelo
    await asyncio.gather(
        test_websocket(),
        test_api_call()
    )

if __name__ == "__main__":
    asyncio.run(main())