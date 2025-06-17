from instaprice import Instaprice
import os

if __name__ == "__main__":
    # Caminho para o arquivo ZIP
    caminho_zip = os.path.join(os.path.dirname(__file__), "202401_NFs.zip")
    
    # Pergunta exemplo para análise das notas fiscais
    pergunta = "Quais são os principais fornecedores e o valor total das notas fiscais?"
    
    # Contexto inicial para as tarefas
    inputs = {
        'caminho_zip': caminho_zip,
        'pergunta_usuario': pergunta,
        'diretorio_dados': os.path.join(os.path.dirname(__file__), 'dados', 'notasfiscais')
    }
    
    # Executa a crew
    instaprice = Instaprice()
    result = instaprice.crew().kickoff(inputs=inputs)
    print(f"Resultado final da Crew: {result}")
