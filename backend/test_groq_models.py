#!/usr/bin/env python3
"""
Script para testar todos os modelos Groq disponíveis
"""

import os
import asyncio
import json
from typing import List, Dict
import groq
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Lista de modelos para testar
MODELS_TO_TEST = [
    # Modelos Llama
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile", 
    "llama-3.1-8b-instant",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    
    # Modelos Meta Llama 4
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruc",
    
    # Modelos Guard
    "meta-llama/llama-guard-4-12bt",
    "meta-llama/llama-guard-4-12b",
    
    # Modelos Qwen
    "qwen-qwq-32b",
    "qwen/qwen3-32b",
    
    # Modelos DeepSeek
    "deepseek-r1-distill-llama-70b",
    
    # Outros modelos
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

async def test_model(client: groq.Groq, model_name: str) -> Dict:
    """Testa um modelo específico"""
    try:
        print(f"🧪 Testando {model_name}...")
        
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Teste de conexão. Responda apenas 'OK' seguido do nome do modelo."
                }
            ],
            model=model_name,
            max_tokens=20,
            temperature=0.1
        )
        
        response_text = completion.choices[0].message.content.strip()
        usage = completion.usage if hasattr(completion, 'usage') else None
        
        print(f"✅ {model_name}: {response_text}")
        
        return {
            "model": model_name,
            "status": "success",
            "response": response_text,
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else None,
                "completion_tokens": usage.completion_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None
            } if usage else None
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"❌ {model_name}: {error_message}")
        
        # Categoriza o erro
        if "authentication" in error_message.lower() or "invalid" in error_message.lower():
            error_type = "auth_error"
        elif "not found" in error_message.lower() or "does not exist" in error_message.lower():
            error_type = "model_not_found" 
        elif "rate limit" in error_message.lower() or "quota" in error_message.lower():
            error_type = "rate_limit"
        else:
            error_type = "unknown_error"
            
        return {
            "model": model_name,
            "status": "error",
            "error": error_message,
            "error_type": error_type
        }

async def test_all_models():
    """Testa todos os modelos da lista"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY não encontrada no arquivo .env")
        return
    
    print(f"🚀 Iniciando teste de {len(MODELS_TO_TEST)} modelos Groq...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print("="*60)
    
    # Cria cliente Groq
    client = groq.Groq(api_key=api_key)
    
    results = []
    successful_models = []
    failed_models = []
    
    for i, model in enumerate(MODELS_TO_TEST, 1):
        print(f"\n[{i}/{len(MODELS_TO_TEST)}]", end=" ")
        
        result = await test_model(client, model)
        results.append(result)
        
        if result["status"] == "success":
            successful_models.append(result)
        else:
            failed_models.append(result)
        
        # Pausa entre testes para evitar rate limiting
        if i < len(MODELS_TO_TEST):
            await asyncio.sleep(1)
    
    # Relatório final
    print("\n" + "="*60)
    print(f"📊 RELATÓRIO FINAL")
    print("="*60)
    print(f"✅ Modelos disponíveis: {len(successful_models)}")
    print(f"❌ Modelos com erro: {len(failed_models)}")
    print(f"📈 Taxa de sucesso: {len(successful_models)/len(MODELS_TO_TEST)*100:.1f}%")
    
    # Modelos disponíveis
    if successful_models:
        print(f"\n🟢 MODELOS DISPONÍVEIS ({len(successful_models)}):")
        for model in successful_models:
            response = model["response"][:50] + "..." if len(model["response"]) > 50 else model["response"]
            print(f"  ✅ {model['model']}: {response}")
    
    # Modelos com erro
    if failed_models:
        print(f"\n🔴 MODELOS COM ERRO ({len(failed_models)}):")
        
        # Agrupa por tipo de erro
        error_groups = {}
        for model in failed_models:
            error_type = model.get("error_type", "unknown")
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(model)
        
        for error_type, models in error_groups.items():
            print(f"\n  📋 {error_type.upper()} ({len(models)}):")
            for model in models:
                print(f"    ❌ {model['model']}: {model['error'][:100]}")
    
    # Salva resultados em arquivo JSON
    output_file = "groq_models_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": str(asyncio.get_event_loop().time()),
            "total_models": len(MODELS_TO_TEST),
            "successful_count": len(successful_models),
            "failed_count": len(failed_models),
            "success_rate": len(successful_models)/len(MODELS_TO_TEST)*100,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    return results

if __name__ == "__main__":
    print("🧪 TESTE GROQ MODELS - INSTAPRICE")
    print("="*60)
    
    # Executa o teste
    results = asyncio.run(test_all_models())