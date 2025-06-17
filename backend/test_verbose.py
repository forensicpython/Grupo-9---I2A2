#!/usr/bin/env python3
"""
Script de teste para verificar captura verbose do CrewAI
"""

import sys
import os

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

from instaprice import Instaprice

def test_verbose_capture():
    """Testa se o verbose está funcionando"""
    
    print("🚀 Iniciando teste verbose do CrewAI...")
    
    # Instancia o Instaprice
    instaprice = Instaprice()
    
    # Prepara inputs de teste
    inputs = {
        'caminho_zip': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/uploads/dados/202401_NFs.zip',
        'pergunta_usuario': 'Teste rápido para verificar verbose',
        'diretorio_dados': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/uploads/dados/notasfiscais'
    }
    
    print("📋 Configurações:")
    print(f"   • Arquivo: {inputs['caminho_zip']}")
    print(f"   • Pergunta: {inputs['pergunta_usuario']}")
    print(f"   • Diretório: {inputs['diretorio_dados']}")
    print()
    
    try:
        print("🤖 Executando crew com verbose=True...")
        print("=" * 60)
        
        # Executa o crew - isso deve gerar muito output verbose
        resultado = instaprice.crew().kickoff(inputs=inputs)
        
        print("=" * 60)
        print("✅ Teste concluído!")
        print(f"📊 Resultado: {str(resultado)[:200]}...")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_verbose_capture()