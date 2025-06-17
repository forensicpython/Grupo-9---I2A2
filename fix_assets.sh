#!/bin/bash

echo "🔧 Corrigindo Assets do Instaprice..."
echo "=================================="

# Muda para o diretório do projeto
cd "$(dirname "$0")"

# Verifica se o logo principal existe
if [ -f "images/Instaprice.png" ]; then
    echo "✅ Logo principal encontrado: images/Instaprice.png"
    
    # Copia para os locais necessários
    echo "📋 Copiando logo para assets frontend..."
    cp "images/Instaprice.png" "frontend/src/assets/instaprice.png"
    cp "images/Instaprice.png" "frontend/src/assets/Instaprice_2.png"
    
    echo "✅ Assets copiados com sucesso!"
else
    echo "❌ Erro: Arquivo images/Instaprice.png não encontrado!"
    echo "Verifique se o logo existe no diretório images/"
    exit 1
fi

# Verifica os assets no frontend
echo "🔍 Verificando assets no frontend..."
if [ -f "frontend/src/assets/instaprice.png" ] && [ -f "frontend/src/assets/Instaprice_2.png" ]; then
    echo "✅ Todos os assets estão presentes!"
else
    echo "❌ Alguns assets estão faltando!"
    ls -la frontend/src/assets/
    exit 1
fi

# Lista os assets disponíveis
echo ""
echo "📁 Assets disponíveis:"
ls -la frontend/src/assets/ | grep -E "\.(png|jpg|jpeg|svg)$"

echo ""
echo "✅ Assets corrigidos! Agora você pode executar ./start.sh"