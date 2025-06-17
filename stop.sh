#!/bin/bash

echo "🛑 Parando Sistema Instaprice..."
echo "================================"

# Para processos por porta
echo "🧹 Matando processos nas portas 8000 e 5173..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null || true

# Para processos por nome
echo "🧹 Matando processos por nome..."
pkill -f 'python server.py' 2>/dev/null || true
pkill -f 'npm run dev' 2>/dev/null || true
pkill -f 'vite' 2>/dev/null || true

# Aguarda um pouco
sleep 2

# Verifica se as portas estão livres
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️ Aviso: Porta 8000 ainda está em uso"
else
    echo "✅ Porta 8000 liberada"
fi

if lsof -ti:5173 >/dev/null 2>&1; then
    echo "⚠️ Aviso: Porta 5173 ainda está em uso"
else
    echo "✅ Porta 5173 liberada"
fi

echo "✅ Sistema parado com sucesso!"