#!/bin/bash

echo "🚀 Iniciando Sistema Hanotas..."

# Muda para o diretório do projeto
cd "$(dirname "$0")"

# Limpa processos antigos
echo "🧹 Limpando processos antigos..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Inicia backend em background
echo "📡 Iniciando backend..."
cd backend
python server.py &
BACKEND_PID=$!

# Aguarda um pouco para o backend iniciar
sleep 3

# Inicia frontend
echo "⚛️ Iniciando frontend..."
cd ../frontend
npm run dev &
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