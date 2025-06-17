#!/usr/bin/env python3
"""
Teste para verificar se o sistema de verbose sem duplicação está funcionando
"""

import os
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from subprocess_runner import run_crewai_subprocess

async def test_verbose_system():
    """Testa o sistema de verbose sem duplicação"""
    
    print("🧪 Testando sistema de verbose sem duplicação...")
    print("="*60)
    
    # Verifica se arquivo ZIP existe
    zip_path = Path(__file__).parent / "202401_NFs.zip"
    if not zip_path.exists():
        print(f"❌ Arquivo ZIP não encontrado: {zip_path}")
        return False
    
    # Prepara inputs de teste
    test_inputs = {
        'caminho_zip': str(zip_path.absolute()),
        'pergunta_usuario': 'Teste do sistema verbose - mostre os 3 maiores compradores',
        'diretorio_dados': str(Path(__file__).parent / "dados" / "notasfiscais")
    }
    
    print(f"📁 Arquivo ZIP: {test_inputs['caminho_zip']}")
    print(f"❓ Pergunta: {test_inputs['pergunta_usuario']}")
    print(f"📂 Diretório: {test_inputs['diretorio_dados']}")
    print("-"*60)
    
    try:
        # Executa subprocess com logs verbose
        print("🚀 Iniciando execução com logs verbose...")
        result = await run_crewai_subprocess(test_inputs, websocket_manager=None)
        
        print("-"*60)
        print("✅ Teste concluído!")
        print(f"📊 Sucesso: {result['success']}")
        
        if result['success']:
            print(f"📝 Resposta final: {result['result'][:100]}...")
            print(f"📋 Total de linhas no log: {len(result['output_lines'])}")
        else:
            print(f"❌ Erro: {result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_verbose_system())
    if success:
        print("\n🎉 Sistema de verbose sem duplicação funcionando!")
    else:
        print("\n⚠️ Ainda há problemas no sistema.")