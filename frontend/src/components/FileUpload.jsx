import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X } from 'lucide-react'
import { filesAPI } from '../services/api'

const FileUpload = ({ onFileUpload, onLog }) => {
  const onDrop = useCallback(async (acceptedFiles) => {
    console.log('FileUpload: onDrop chamado com arquivos:', acceptedFiles)
    onLog(`🎯 Arquivos detectados: ${acceptedFiles.length}`, 'info')
    
    for (const file of acceptedFiles) {
      try {
        onLog(`📤 Enviando arquivo: ${file.name} (${file.size} bytes)`, 'info')
        console.log('FileUpload: Enviando arquivo:', file)
        
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await filesAPI.upload(formData, (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onLog(`📊 Upload ${file.name}: ${progress}%`, 'info')
        })
        
        console.log('FileUpload: Resposta do servidor:', response)
        onLog(`✅ Arquivo enviado: ${file.name}`, 'success')
        
        // Chama callback original com dados do servidor
        const fileData = {
          ...file,
          id: response.data.file_id,
          serverResponse: response.data
        }
        console.log('FileUpload: Chamando onFileUpload com:', fileData)
        onFileUpload([fileData])
        
      } catch (error) {
        console.error('FileUpload: Erro no upload:', error)
        onLog(`❌ Erro no upload de ${file.name}: ${error.message}`, 'error')
      }
    }
  }, [onFileUpload, onLog])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 10,
    maxSize: 100 * 1024 * 1024 // 100MB
  })

  const getBorderColor = () => {
    if (isDragAccept) return 'border-green-500 bg-green-500/10'
    if (isDragReject) return 'border-red-500 bg-red-500/10'
    if (isDragActive) return 'border-instaprice-primary bg-instaprice-primary/10'
    return 'border-gray-600 hover:border-instaprice-primary/50'
  }

  return (
    <div className="glass-effect rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Upload className="w-5 h-5 mr-2" />
        Envie seus arquivos e faça perguntas inteligentes
      </h3>
      
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-300 ${getBorderColor()}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-instaprice-primary/20 rounded-full 
                         flex items-center justify-center">
            <Upload className="w-8 h-8 text-instaprice-primary" />
          </div>
          
          <div>
            <p className="text-white font-medium mb-2">
              {isDragActive 
                ? 'Solte seus arquivos aqui...' 
                : 'Arraste e solte seu arquivo aqui'
              }
            </p>
            <p className="text-gray-400 text-sm">
              ou clique para selecionar
            </p>
          </div>
          
          <div className="flex justify-center space-x-4 text-xs">
            <div className="flex items-center space-x-1 text-gray-400">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>ZIP</span>
            </div>
            <div className="flex items-center space-x-1 text-gray-400">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>CSV</span>
            </div>
            <div className="flex items-center space-x-1 text-gray-400">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span>XLSX</span>
            </div>
          </div>
          
          <p className="text-xs text-gray-500">
            Máximo: 100MB • Múltiplos arquivos permitidos
          </p>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-gray-400">
        <p className="font-medium mb-1">Formatos suportados:</p>
        <ul className="list-disc list-inside space-y-1 text-gray-500">
          <li>Arquivos ZIP com notas fiscais</li>
          <li>Planilhas CSV com dados estruturados</li>
          <li>Arquivos Excel (.xlsx, .xls)</li>
        </ul>
      </div>
    </div>
  )
}

export default FileUpload