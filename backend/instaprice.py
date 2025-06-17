from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai.llm import LLM
import sys
import os

# Importa as tools personalizadas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from tools.zip_extractor_tool import zip_extractor_tool
from tools.csv_validator_tool import csv_validator_tool
from tools.pandas_query_tool import pandas_query_executor_tool
from tools.rag_tool import rag_semantic_search_tool

# Carrega variáveis de ambiente - busca em múltiplos locais
env_paths = ['.env', '../.env', os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')]
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
modelo_llm = os.getenv("MODEL", "llama-3.1-8b-instant")

# Configuração robusta do LLM com tratamento de erro
try:
    llm = LLM(
        model=f"groq/{modelo_llm}",
        api_key=groq_api_key,
        temperature=0.1,  # Mais determinista
        max_tokens=3000   # Aumentado para respostas completas
    )
except Exception as e:
    print(f"⚠️ Erro na configuração do LLM: {e}")
    print(f"🔄 Tentando configuração alternativa...")
    llm = LLM(
        model=f"groq/{modelo_llm}",
        api_key=groq_api_key
    )

@CrewBase
class Instaprice:
    """Sistema Inteligente de Análise de Notas Fiscais usando CrewAI"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def zip_desbravador(self) -> Agent:
        """Agente especialista em extração de arquivos compactados"""
        return Agent(
            config=self.agents_config['zip_desbravador'],
            llm=llm,
            tools=[zip_extractor_tool],
            verbose=True
        )

    @agent
    def guardiao_pydantic(self) -> Agent:
        """Agente validador e estruturador de dados usando Pydantic"""
        return Agent(
            config=self.agents_config['guardiao_pydantic'],
            llm=llm,
            tools=[csv_validator_tool],
            verbose=True
        )

    @agent
    def linguista_lucido(self) -> Agent:
        """Agente intérprete de perguntas em linguagem natural"""
        return Agent(
            config=self.agents_config['linguista_lucido'],
            llm=llm,
            tools=[rag_semantic_search_tool],
            verbose=True
        )

    @agent
    def executor_de_consultas(self) -> Agent:
        """Agente executor de operações Pandas sobre dados validados"""
        return Agent(
            config=self.agents_config['executor_de_consultas'],
            llm=llm,
            tools=[pandas_query_executor_tool],
            verbose=True
        )

    @agent
    def rp_ludico(self) -> Agent:
        """Agente comunicador que gera respostas humanizadas e divertidas"""
        return Agent(
            config=self.agents_config['rp_ludico'],
            llm=llm,
            verbose=True
        )

    @agent
    def sugestor_visionario(self) -> Agent:
        """Agente que sugere novas perguntas relevantes"""
        return Agent(
            config=self.agents_config['sugestor_visionario'],
            llm=llm,
            verbose=True
        )

    @agent
    def porta_voz_eloquente(self) -> Agent:
        """Agente embaixador final responsável pela resposta definitiva ao usuário"""
        return Agent(
            config=self.agents_config['porta_voz_eloquente'],
            llm=llm,
            verbose=True
        )

    @task
    def extracao_task(self) -> Task:
        """Tarefa de extração de arquivos ZIP"""
        return Task(
            config=self.tasks_config['extracao_task'],
            agent=self.zip_desbravador()
        )

    @task
    def validacao_task(self) -> Task:
        """Tarefa de validação e estruturação com Pydantic"""
        return Task(
            config=self.tasks_config['validacao_task'],
            agent=self.guardiao_pydantic(),
            context=[self.extracao_task()]
        )

    @task
    def interpretacao_task(self) -> Task:
        """Tarefa de interpretação de linguagem natural"""
        return Task(
            config=self.tasks_config['interpretacao_task'],
            agent=self.linguista_lucido(),
            context=[self.validacao_task()]
        )

    @task
    def execucao_task(self) -> Task:
        """Tarefa de execução de consultas Pandas"""
        return Task(
            config=self.tasks_config['execucao_task'],
            agent=self.executor_de_consultas(),
            context=[self.interpretacao_task()]
        )

    @task
    def comunicacao_task(self) -> Task:
        """Tarefa de comunicação humanizada dos resultados"""
        return Task(
            config=self.tasks_config['comunicacao_task'],
            agent=self.rp_ludico(),
            context=[self.execucao_task()]
        )

    @task
    def sugestoes_task(self) -> Task:
        """Tarefa de geração de sugestões inteligentes"""
        return Task(
            config=self.tasks_config['sugestoes_task'],
            agent=self.sugestor_visionario(),
            context=[self.comunicacao_task()]
        )

    @task
    def resposta_final_task(self) -> Task:
        """Tarefa final do Porta-Voz Eloquente para resposta definitiva"""
        return Task(
            config=self.tasks_config['resposta_final_task'],
            agent=self.porta_voz_eloquente(),
            context=[self.comunicacao_task(), self.sugestoes_task()],
            output_file="resposta_final_porta_voz.md"
        )

    @crew
    def crew(self) -> Crew:
        """Configura e retorna a crew completa do Instaprice com novo Porta-Voz"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False  # Desabilitado temporariamente para evitar erros de HTTP
        )

