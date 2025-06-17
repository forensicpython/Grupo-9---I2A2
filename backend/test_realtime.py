#!/usr/bin/env python3
"""
Teste simples para verificar captura de logs em tempo real
"""

import sys
import os
import asyncio
import time

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

class MockManager:
    """Manager fake para testes"""
    
    async def broadcast(self, message):
        print(f"📡 WebSocket: {message['data']['message'].strip()}")

async def test_log_capture():
    """Testa se a captura está funcionando"""
    
    from server import RealTimeLogCapture
    
    print("🧪 Testando captura de logs em tempo real...")
    
    # Cria manager fake
    mock_manager = MockManager()
    
    # Configura capturador
    log_capture = RealTimeLogCapture()
    log_capture.set_manager(mock_manager)
    
    print("🚀 Iniciando captura...")
    log_capture.start_capture()
    
    try:
        # Simula outputs que o CrewAI faria
        print("Teste 1: Print simples")
        print("Teste 2: Print com múltiplas")
        print("linhas")
        print("Teste 3: Print final")
        
        # Aguarda um pouco para processar
        await asyncio.sleep(0.5)
        
        print("✅ Teste de captura concluído!")
        
    finally:
        log_capture.stop_capture()
        print("🔄 Captura finalizada")

if __name__ == "__main__":
    asyncio.run(test_log_capture())