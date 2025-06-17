#!/usr/bin/env python3
"""
Runner para executar CrewAI em processo separado e capturar output real
"""

import sys
import os
import subprocess
import asyncio
import json
from datetime import datetime

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

async def run_instaprice_with_output(inputs, websocket_manager=None):
    """
    Executa o Instaprice em subprocess e captura output real do terminal
    """
    try:
        # Cria script temporário para execução
        script_content = f"""
import sys
import os
sys.path.insert(0, '{os.path.dirname(__file__)}')

from instaprice import Instaprice
import json

# Inputs recebidos
inputs = {repr(inputs)}

print("🚀 Iniciando execução do CrewAI...")
print(f"📋 Inputs: {{inputs}}")
print("=" * 60)

# Instancia e executa
instaprice = Instaprice()
resultado = instaprice.crew().kickoff(inputs=inputs)

print("=" * 60)
print("✅ Execução concluída!")
print(f"📊 Resultado: {{str(resultado)[:200]}}...")
"""
        
        # Salva script temporário
        script_path = "/tmp/instaprice_runner.py"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Executa o script e captura output em tempo real
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream do output em tempo real
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                
                # Envia para WebSocket se disponível
                if websocket_manager:
                    await websocket_manager.broadcast({
                        "type": "agent_log",
                        "data": {
                            "message": output,  # Output real com quebras de linha
                            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "raw_terminal": True
                        }
                    })
                
                print(output, end='')  # Também imprime no console atual
        
        # Aguarda conclusão
        process.wait()
        
        # Remove script temporário
        os.remove(script_path)
        
        return {
            "success": True,
            "output": "\\n".join(output_lines),
            "return_code": process.returncode
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": ""
        }

if __name__ == "__main__":
    # Teste direto
    test_inputs = {
        'caminho_zip': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/202401_NFs.zip',
        'pergunta_usuario': 'Teste de captura de terminal em tempo real',
        'diretorio_dados': '/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/Instaprice_2/backend/dados/notasfiscais'
    }
    
    async def test():
        result = await run_instaprice_with_output(test_inputs)
        print(f"Resultado: {result}")
    
    asyncio.run(test())