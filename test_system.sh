#!/bin/bash

echo "🧪 Testando Sistema Instaprice..."
echo "=================================="

# Muda para o diretório do projeto
cd "$(dirname "$0")"

# Inicia o sistema em background
echo "🚀 Iniciando sistema..."
./start.sh &
START_PID=$!

# Aguarda os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem (30 segundos)..."
sleep 30

# Testa backend
echo "🔍 Testando backend..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend está funcionando!"
    curl -s http://localhost:8000/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Backend não está respondendo!"
fi

# Testa frontend
echo "🔍 Testando frontend..."
if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo "✅ Frontend está funcionando!"
else
    echo "❌ Frontend não está respondendo!"
fi

# Testa API docs
echo "🔍 Testando API docs..."
if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
    echo "✅ API docs está funcionando!"
else
    echo "❌ API docs não está respondendo!"
fi

echo ""
echo "🎯 Teste concluído!"
echo "📡 Acesse: http://localhost:5173 (Frontend)"
echo "🔧 Acesse: http://localhost:8000 (API)"
echo "📚 Acesse: http://localhost:8000/docs (Documentação)"
echo ""
echo "💡 Para parar o sistema, execute:"
echo "   pkill -f 'python server.py'"
echo "   pkill -f 'npm run dev'"

# Para o sistema após o teste
echo "🛑 Parando sistema de teste..."
kill $START_PID 2>/dev/null
pkill -f 'python server.py' 2>/dev/null
pkill -f 'npm run dev' 2>/dev/null

echo "✅ Teste finalizado!"