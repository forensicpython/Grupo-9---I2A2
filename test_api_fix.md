# 🔧 Correção da API Instaprice

## ✅ **Problema Identificado**

O erro `Invalid API Key` ocorreu porque:

1. **Backend não recebia a chave API** configurada na interface web
2. **Frontend não enviava** as credenciais no processamento
3. Sistema usava apenas a chave fixa do `.env`

## 🛠️ **Correções Implementadas**

### 1. **Backend** (`server.py`)

#### Novo modelo de request:
```python
class ProcessRequest(BaseModel):
    apiKey: str
    model: str
    pergunta: str = "Analise os dados das notas fiscais"
```

#### Endpoint atualizado:
```python
@app.post("/api/process/{file_id}")
async def process_file(file_id: str, request: ProcessRequest):
    # Configura a chave API dinamicamente
    os.environ["GROQ_API_KEY"] = request.apiKey
    
    inputs = {
        'caminho_zip': str(file_path.absolute()),
        'pergunta_usuario': request.pergunta,
        'diretorio_dados': str(dados_dir.absolute())
    }
```

### 2. **Frontend** (`api.js`)

#### API atualizada:
```javascript
process: (fileId, pergunta, apiKey, model) => {
  return longApi.post(`/api/process/${fileId}`, {
    apiKey: apiKey,
    model: model,
    pergunta: pergunta
  }, {
    timeout: TIMEOUTS.API.PROCESSING,
  })
}
```

### 3. **AnalysisPage** (`AnalysisPage.jsx`)

#### Chamada corrigida:
```javascript
response = await filesAPI.process(
  analysisData.file.serverFileId, 
  message,
  analysisData.apiKey,  // ✅ Agora envia a chave
  analysisData.model    // ✅ Agora envia o modelo
)
```

## 🔄 **Fluxo Corrigido**

1. **Usuário configura API** no Dashboard → `ApiTest`
2. **Dashboard salva** `apiKey` e `model` → `handleApiConfigured`
3. **Upload do arquivo** → FileUpload
4. **Usuário clica "Analisar"** → Dashboard salva no localStorage
5. **AnalysisPage carrega** dados do localStorage
6. **Primeira pergunta** → envia `apiKey` e `model` para backend
7. **Backend configura** `GROQ_API_KEY` dinamicamente
8. **CrewAI executa** com a chave correta

## 🎯 **Próximos Passos**

1. **Teste com chave válida** na interface de configuração
2. **Faça upload** de um arquivo ZIP
3. **Digite sua pergunta**: "quantas notas nós temos com valor acima de R$5000,00"
4. **Monitore** o terminal verbose integrado

## ⚠️ **Importante**

- A chave API deve ser configurada **sempre** antes do processamento
- O sistema agora usa a chave da **interface web**, não do `.env`
- Verifique se sua chave Groq está **válida** em https://console.groq.com