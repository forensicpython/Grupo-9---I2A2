#!/bin/bash

echo "🚀 Iniciando Sistema Instaprice..."
echo "=================================================="

# Muda para o diretório do projeto
cd "$(dirname "$0")"

# Verifica se os diretórios existem
if [ ! -d "backend" ]; then
    echo "❌ Erro: Diretório 'backend' não encontrado!"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Erro: Diretório 'frontend' não encontrado!"
    exit 1
fi

# Corrige assets automaticamente
echo "🔧 Verificando e corrigindo assets..."
if [ ! -f "frontend/src/assets/instaprice.png" ] || [ ! -f "frontend/src/assets/Instaprice_2.png" ]; then
    echo "⚠️ Assets faltando. Corrigindo automaticamente..."
    ./fix_assets.sh
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao corrigir assets!"
        exit 1
    fi
else
    echo "✅ Assets estão presentes"
fi

# Limpa processos antigos
echo "🧹 Limpando processos antigos..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 2

# Verifica se as portas estão livres
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "❌ Erro: Porta 8000 ainda está em uso!"
    exit 1
fi

if lsof -ti:5173 >/dev/null 2>&1; then
    echo "❌ Erro: Porta 5173 ainda está em uso!"
    exit 1
fi

# Verifica dependências do backend
echo "🔍 Verificando dependências do backend..."
cd backend
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "❌ Erro: Dependências do backend não instaladas!"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

# Verifica se o módulo instaprice existe
if ! python -c "import instaprice" 2>/dev/null; then
    echo "❌ Erro: Módulo instaprice não encontrado!"
    exit 1
fi

# Inicia backend em background
echo "📡 Iniciando backend..."
python server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Aguarda backend inicializar
echo "⏳ Aguardando backend inicializar..."
sleep 5

# Verifica se o backend está respondendo
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "⚠️ Backend pode não ter iniciado corretamente. Verificando logs..."
    tail -10 ../logs/backend.log 2>/dev/null || echo "Nenhum log encontrado"
fi

# Verifica dependências do frontend
echo "🔍 Verificando dependências do frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "❌ Erro: node_modules não encontrado!"
    echo "Execute: npm install"
    exit 1
fi

# Inicia frontend
echo "⚛️ Iniciando frontend..."
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✅ Sistema iniciado!"
echo "📡 Backend: http://localhost:8000"
echo "⚛️ Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Para parar o sistema, pressione Ctrl+C"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando sistema..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Sistema parado!"
    exit 0
}

# Captura Ctrl+C
trap cleanup INT

# Mantém o script rodando
wait