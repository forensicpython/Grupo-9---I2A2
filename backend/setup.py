#!/usr/bin/env python3
"""
Setup script para o projeto Instaprice
Configura o ambiente e instala dependências
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step_name, status="EXECUTANDO"):
    icons = {"EXECUTANDO": "⏳", "SUCESSO": "✅", "ERRO": "❌", "AVISO": "⚠️"}
    print(f"{icons.get(status, '❓')} {step_name}")

def run_command(command, description):
    """Executa comando e retorna resultado"""
    print_step(description)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_step(description, "SUCESSO")
            return True, result.stdout
        else:
            print_step(f"{description} - {result.stderr}", "ERRO")
            return False, result.stderr
    except Exception as e:
        print_step(f"{description} - {str(e)}", "ERRO")
        return False, str(e)

def main():
    print_header("INSTAPRICE SETUP - CONFIGURAÇÃO DO AMBIENTE")
    
    # Verifica Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print_step("Python 3.8+ é necessário", "ERRO")
        sys.exit(1)
    
    print_step(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}", "SUCESSO")
    
    # Instala dependências
    print_header("INSTALANDO DEPENDÊNCIAS")
    success, output = run_command("pip install -r requirements.txt", "Instalando pacotes Python")
    
    if not success:
        print("Tentando instalar individualmente...")
        packages = ["crewai", "python-dotenv", "pandas", "pydantic", "sentence-transformers"]
        for pkg in packages:
            run_command(f"pip install {pkg}", f"Instalando {pkg}")
    
    # Cria estrutura de diretórios
    print_header("CRIANDO ESTRUTURA DE DIRETÓRIOS")
    
    dirs_to_create = [
        "dados/notasfiscais",
        "logs",
        "output"
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print_step(f"Diretório {dir_path} criado/verificado", "SUCESSO")
    
    # Verifica arquivo .env em múltiplos locais
    print_header("CONFIGURANDO VARIÁVEIS DE AMBIENTE")
    
    env_paths = ['.env', '../.env']
    env_found = False
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print_step(f"Arquivo .env encontrado em: {env_path}", "SUCESSO")
            env_found = True
            break
    
    if not env_found:
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print_step("Arquivo .env criado a partir do .env.example", "SUCESSO")
            print_step("CONFIGURE sua GROQ_API_KEY no arquivo .env", "AVISO")
        elif os.path.exists("../.env.example"):
            shutil.copy("../.env.example", "../.env")
            print_step("Arquivo .env criado no diretório pai", "SUCESSO")
            print_step("CONFIGURE sua GROQ_API_KEY no arquivo .env", "AVISO")
        else:
            print_step("Arquivo .env.example não encontrado", "ERRO")
    
    # Executa teste de validação
    print_header("EXECUTANDO TESTES DE VALIDAÇÃO")
    success, output = run_command("python test_instaprice.py", "Validando configuração do projeto")
    
    if success:
        print_step("Projeto configurado com sucesso!", "SUCESSO")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Configure sua GROQ_API_KEY no arquivo .env")
        print("2. Execute: python main_1.py")
        print("3. Monitore os logs de execução")
    else:
        print_step("Configuração apresentou problemas", "AVISO")
        print("\n🔧 VERIFIQUE:")
        print("1. Variáveis de ambiente no arquivo .env")
        print("2. Dependências instaladas corretamente")
        print("3. Execute: python test_instaprice.py para diagnóstico")

if __name__ == "__main__":
    main()