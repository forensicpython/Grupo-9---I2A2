"""
🕵️ OPERAÇÃO GRAMPO DIGITAL - Sistema de Vigilância de Agentes Instaprice
====================================================================

Módulo ultra-secreto para interceptação e documentação de conversas entre agentes.
Código de codinome: "EAVESDROP" (Espionagem Avançada e Vigilância Eletrônica de Sistemas de Processamento)

⚠️ CONFIDENCIAL - APENAS PARA INVESTIGADORES AUTORIZADOS ⚠️
"""

import os
import io
import sys
from datetime import datetime
from typing import List, Dict, Any
from contextlib import redirect_stdout, redirect_stderr
import re

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.colors import black, red, blue, green, orange
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class EspionDigital:
    """
    🔍 Interceptador de Conversas de Agentes AI
    
    Sistema de vigilância para monitoramento e documentação de todas as
    interações entre agentes do sistema Instaprice. Código nome: "WIRE_TAP_AI"
    """
    
    def __init__(self):
        self.conversas_interceptadas = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.agente_atual = None
        self.buffer_conversa = io.StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.interceptacao_ativa = False
        
    def iniciar_grampo(self):
        """🎧 Inicia a interceptação das comunicações entre agentes"""
        self.interceptacao_ativa = True
        self.conversas_interceptadas.append({
            'timestamp': datetime.now(),
            'evento': 'INICIO_OPERACAO_GRAMPO',
            'detalhes': f'Sessão de espionagem iniciada - ID: {self.session_id}',
            'agente': 'SISTEMA_VIGILANCIA'
        })
        
    def capturar_conversa_agente(self, nome_agente: str, acao: str, conteudo: str):
        """
        🕵️ Captura e registra uma conversa específica de um agente
        
        Args:
            nome_agente: Nome do agente sendo monitorado
            acao: Tipo de ação (Thought, Tool, Final Answer, etc.)
            conteudo: Conteúdo da comunicação interceptada
        """
        if not self.interceptacao_ativa:
            return
            
        registro_interceptado = {
            'timestamp': datetime.now(),
            'agente': nome_agente,
            'acao': acao,
            'conteudo': conteudo,
            'evento': 'COMUNICACAO_INTERCEPTADA'
        }
        
        self.conversas_interceptadas.append(registro_interceptado)
        
    def processar_log_crewai(self, log_texto: str):
        """
        🔍 Processa logs do CrewAI para extrair conversas dos agentes
        
        Args:
            log_texto: Texto completo dos logs do CrewAI
        """
        if not self.interceptacao_ativa:
            return
            
        # Padrões regex para interceptar diferentes tipos de comunicação
        patterns = {
            'agent_section': r'# Agent:\s*([^\n]+)',
            'task_section': r'## Task:\s*([^\n]+)',
            'thought': r'## Thought:\s*([^#]+?)(?=##|$)',
            'tool_usage': r'## Using tool:\s*([^\n]+)',
            'tool_input': r'## Tool Input:\s*([^#]+?)(?=##|$)',
            'tool_output': r'## Tool Output:\s*([^#]+?)(?=##|$)',
            'final_answer': r'## Final Answer:\s*([^#]+?)(?=##|#|$)'
        }
        
        linhas = log_texto.split('\n')
        agente_atual = "AGENTE_DESCONHECIDO"
        
        for linha in linhas:
            # Detecta mudança de agente
            agent_match = re.search(patterns['agent_section'], linha)
            if agent_match:
                agente_atual = agent_match.group(1).strip()
                self.capturar_conversa_agente(agente_atual, "IDENTIFICACAO", f"Agente identificado: {agente_atual}")
                continue
                
            # Detecta task
            task_match = re.search(patterns['task_section'], linha)
            if task_match:
                self.capturar_conversa_agente(agente_atual, "TASK", task_match.group(1).strip())
                continue
        
        # Processa seções maiores
        for tipo, pattern in patterns.items():
            if tipo in ['agent_section', 'task_section']:
                continue
                
            matches = re.finditer(pattern, log_texto, re.MULTILINE | re.DOTALL)
            for match in matches:
                conteudo = match.group(1).strip()
                if conteudo:
                    self.capturar_conversa_agente(agente_atual, tipo.upper(), conteudo)
    
    def processar_conversas_completas(self, texto_completo: str):
        """
        🎯 Processa texto completo do terminal para extrair conversas EXATAS dos agentes
        
        Args:
            texto_completo: Todo o texto que apareceu no terminal
        """
        if not self.interceptacao_ativa:
            return
            
        # Divide o texto em seções por agente
        secoes_agentes = re.split(r'(?=# Agent:)', texto_completo)
        
        for secao in secoes_agentes:
            if not secao.strip():
                continue
                
            # Extrai nome do agente
            agent_match = re.search(r'# Agent:\s*([^\n]+)', secao)
            if not agent_match:
                continue
                
            nome_agente = agent_match.group(1).strip()
            
            # Processa cada tipo de seção dentro do agente
            secoes_tipos = {
                'TASK_ASSIGNMENT': r'## Task:(.*?)(?=##|\Z)',
                'AGENT_THINKING': r'## Thought:(.*?)(?=##|\Z)', 
                'TOOL_USAGE': r'## Using tool:(.*?)(?=##|\Z)',
                'TOOL_INPUT': r'## Tool Input:(.*?)(?=##|\Z)',
                'TOOL_OUTPUT': r'## Tool Output:(.*?)(?=##|\Z)',
                'FINAL_ANSWER': r'## Final Answer:(.*?)(?=##|\Z)'
            }
            
            for tipo_secao, pattern in secoes_tipos.items():
                matches = re.finditer(pattern, secao, re.MULTILINE | re.DOTALL)
                for match in matches:
                    conteudo = match.group(1).strip()
                    if conteudo:
                        # Remove caracteres de controle e formatação desnecessária
                        conteudo_limpo = re.sub(r'\x1b\[[0-9;]*m', '', conteudo)  # Remove códigos ANSI
                        conteudo_limpo = re.sub(r'\[9[0-9]m', '', conteudo_limpo)  # Remove mais códigos de cor
                        
                        self.capturar_conversa_agente(
                            nome_agente,
                            tipo_secao,
                            conteudo_limpo
                        )
    
    def finalizar_grampo(self):
        """🛑 Finaliza a operação de interceptação"""
        self.interceptacao_ativa = False
        self.conversas_interceptadas.append({
            'timestamp': datetime.now(),
            'evento': 'FIM_OPERACAO_GRAMPO',
            'detalhes': f'Operação finalizada. Total de interceptações: {len(self.conversas_interceptadas)}',
            'agente': 'SISTEMA_VIGILANCIA'
        })
        
    def gerar_nome_arquivo_secreto(self) -> str:
        """
        🎭 Gera nomes criativos para o arquivo de espionagem
        
        Returns:
            Nome criativo do arquivo PDF
        """
        nomes_investigativos = [
            f"GRAMPO_DIGITAL_INSTAPRICE_{self.session_id}.pdf",
            f"OPERACAO_EAVESDROP_{self.session_id}.pdf", 
            f"WIRE_TAP_AI_SURVEILLANCE_{self.session_id}.pdf",
            f"INTERCEPTACAO_AGENTES_{self.session_id}.pdf",
            f"CLASSIFIED_AGENT_CHATTER_{self.session_id}.pdf",
            f"ESPIONAGEM_DIGITAL_PROTOCOL_{self.session_id}.pdf",
            f"DOSSIE_CONVERSAS_SECRETAS_{self.session_id}.pdf",
            f"BLACKBOX_AGENT_RECORDING_{self.session_id}.pdf",
            f"UNDERCOVER_AI_MONITORING_{self.session_id}.pdf",
            f"STEALTH_CONVERSATION_LOG_{self.session_id}.pdf"
        ]
        
        # Seleciona um nome baseado no timestamp
        import random
        random.seed(int(self.session_id.replace('_', '')))
        return random.choice(nomes_investigativos)
    
    def gerar_relatorio_pdf(self, caminho_saida: str = None) -> str:
        """
        📋 Gera relatório PDF simples e limpo
        
        Args:
            caminho_saida: Caminho onde salvar o PDF (opcional)
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        if not REPORTLAB_AVAILABLE:
            return self._gerar_relatorio_texto()
            
        if not caminho_saida:
            nome_arquivo = self.gerar_nome_arquivo_secreto()
            caminho_saida = os.path.join(os.getcwd(), nome_arquivo)
        
        # Configuração do documento
        doc = SimpleDocTemplate(
            caminho_saida, 
            pagesize=A4,
            leftMargin=0.8*inch,
            rightMargin=0.8*inch,
            topMargin=0.8*inch,
            bottomMargin=0.8*inch
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Estilos personalizados simples
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,
            textColor=black
        )
        
        subtitulo_style = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=black
        )
        
        agente_style = ParagraphStyle(
            'Agente',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=15,
            textColor=blue,
            fontName='Helvetica-Bold'
        )
        
        acao_style = ParagraphStyle(
            'Acao',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            leftIndent=20,
            textColor=red,
            fontName='Helvetica-Bold'
        )
        
        conteudo_style = ParagraphStyle(
            'Conteudo',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            leftIndent=30,
            fontName='Courier',
            textColor=black
        )
        
        # === CABEÇALHO ===
        story.append(Paragraph("🕵️ OPERAÇÃO GRAMPO DIGITAL", titulo_style))
        story.append(Paragraph("Sistema de Vigilância de Agentes Instaprice", subtitulo_style))
        story.append(Spacer(1, 20))
        
        # === METADADOS ===
        metadata = f"""Código: EAVESDROP-{self.session_id}
Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Total de Interceptações: {len(self.conversas_interceptadas)} comunicações
Status: MISSÃO CONCLUÍDA
Classificação: ULTRA-SECRETO"""
        
        story.append(Paragraph("📊 METADADOS DA OPERAÇÃO", subtitulo_style))
        story.append(Paragraph(metadata, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # === ORGANIZAÇÃO DE DADOS ===
        
        # Organiza conversas por agente
        conversas_por_agente = {}
        eventos_sistema = []
        
        for conversa in self.conversas_interceptadas:
            if conversa.get('evento') in ['INICIO_OPERACAO_GRAMPO', 'FIM_OPERACAO_GRAMPO']:
                eventos_sistema.append(conversa)
            else:
                agente = conversa.get('agente', 'AGENTE_DESCONHECIDO')
                if agente not in conversas_por_agente:
                    conversas_por_agente[agente] = []
                conversas_por_agente[agente].append(conversa)
        
        # === ÍNDICE DE AGENTES ===
        story.append(Paragraph("📑 AGENTES INTERCEPTADOS", subtitulo_style))
        
        for agente in conversas_por_agente.keys():
            emoji_agente = self._get_emoji_para_agente(agente)
            qtd_conversas = len(conversas_por_agente[agente])
            linha_agente = f"• {emoji_agente} {agente} - {qtd_conversas} interceptações"
            story.append(Paragraph(linha_agente, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # === CONVERSAS DOS AGENTES ===
        story.append(PageBreak())
        story.append(Paragraph("💬 TRANSCRIÇÕES DAS CONVERSAS", titulo_style))
        
        for agente, conversas in conversas_por_agente.items():
            # Cabeçalho do agente
            emoji_agente = self._get_emoji_para_agente(agente)
            story.append(Paragraph(f"{emoji_agente} {agente}", agente_style))
            
            # Estatísticas
            inicio = conversas[0]['timestamp'].strftime('%H:%M:%S')
            fim = conversas[-1]['timestamp'].strftime('%H:%M:%S')
            stats = f"📊 {len(conversas)} comunicações | ⏱️ {inicio} - {fim}"
            story.append(Paragraph(stats, styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Processa cada conversa
            for conversa in conversas:
                timestamp_str = conversa['timestamp'].strftime('%H:%M:%S')
                acao = conversa.get('acao', 'COMUNICACAO')
                conteudo = conversa.get('conteudo', 'Conteúdo interceptado indisponível')
                
                # Mapeamento de ações
                mapeamento_acoes = {
                    'TASK_ASSIGNMENT': '📋 Task Received',
                    'AGENT_THINKING': '🧠 Thinking',
                    'TOOL_USAGE': '🔧 Tool',
                    'TOOL_INPUT': '📥 Input',
                    'TOOL_OUTPUT': '📤 Output',
                    'FINAL_ANSWER': '✅ Answer',
                    'AGENT_IDENTIFICATION': '🆔 ID'
                }
                
                nome_acao = mapeamento_acoes.get(acao, f'📡 {acao}')
                
                # Header da ação
                header = f"[{timestamp_str}] {nome_acao}"
                story.append(Paragraph(header, acao_style))
                
                # Conteúdo limpo e simples
                if conteudo and conteudo.strip():
                    conteudo_limpo = self._limpar_texto_simples(conteudo)
                    # Quebra em linhas de 80 caracteres
                    import textwrap
                    linhas = textwrap.wrap(conteudo_limpo, width=80)
                    
                    for linha in linhas:
                        if linha.strip():
                            story.append(Paragraph(linha, conteudo_style))
                
                story.append(Spacer(1, 8))
            
            # Separador entre agentes
            story.append(Spacer(1, 15))
            story.append(Paragraph("―" * 60, styles['Normal']))
            story.append(Spacer(1, 15))
        
        # === RODAPÉ ===
        story.append(PageBreak())
        story.append(Paragraph("🔒 FIM DO RELATÓRIO", titulo_style))
        footer_text = f"""Este documento foi gerado automaticamente pelo sistema de vigilância 
de agentes AI do projeto Instaprice. Todas as comunicações foram 
interceptadas e documentadas conforme protocolo EAVESDROP.

⚠️ CLASSIFICAÇÃO: ULTRA-SECRETO ⚠️
Mantenha este documento em local seguro"""
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Gera o PDF
        doc.build(story)
        
        return caminho_saida
    
    def _get_emoji_para_agente(self, nome_agente: str) -> str:
        """Retorna emoji específico para cada tipo de agente"""
        mapeamento = {
            'Extrator de Arquivos': '📦',
            'Zip Desbravador': '📦', 
            'Validador de Dados': '🛡️',
            'Guardião Pydantic': '🛡️',
            'Intérprete NLP': '🧠',
            'Linguista Lúcido': '🧠',
            'Analista Pandas': '📊',
            'Executor de Consultas': '📊',
            'Comunicador': '💬',
            'RP Lúdico': '💬',
            'Gerador de Insights': '💡',
            'Sugestor Visionário': '💡'
        }
        
        for chave, emoji in mapeamento.items():
            if chave.lower() in nome_agente.lower():
                return emoji
        
        return '🤖'  # Default
    
    def _limpar_texto_simples(self, texto: str) -> str:
        """Limpa texto de forma simples para PDF básico"""
        # Remove códigos ANSI e códigos de cor
        texto = re.sub(r'\x1b\[[0-9;]*m', '', texto)
        texto = re.sub(r'\[9[0-9]m', '', texto)
        texto = re.sub(r'\[\d+m', '', texto)
        
        # Remove caracteres de controle
        texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', texto)
        
        # Remove caracteres problemáticos
        texto = re.sub(r'[<>&"\']', '', texto)
        
        # Substitui quebras de linha por espaços
        texto = texto.replace('\n', ' ')
        texto = texto.replace('\r', ' ')
        texto = texto.replace('\t', ' ')
        
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        # Trunca se muito longo
        if len(texto) > 1000:
            texto = texto[:997] + "..."
        
        return texto.strip()
    
    def _limpar_texto_html(self, texto: str) -> str:
        """Mantido para compatibilidade"""
        return self._limpar_texto_simples(texto)
    
    def _limpar_texto_obsidian(self, texto: str) -> str:
        """Mantido para compatibilidade"""
        return self._limpar_texto_simples(texto)
    
    def _formatar_conteudo_estruturado(self, conteudo: str) -> str:
        """Formata conteúdo estruturado - versão simplificada sem HTML"""
        # Apenas limpa o conteúdo, sem formatação HTML complexa
        return self._limpar_texto_obsidian(conteudo)
    
    def _gerar_relatorio_texto(self) -> str:
        """Fallback para quando reportlab não está disponível"""
        nome_arquivo = self.gerar_nome_arquivo_secreto().replace('.pdf', '.txt')
        caminho_saida = os.path.join(os.getcwd(), nome_arquivo)
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write("🕵️ OPERAÇÃO GRAMPO DIGITAL - INSTAPRICE\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Sessão: {self.session_id}\n")
            f.write(f"Total de interceptações: {len(self.conversas_interceptadas)}\n\n")
            
            for i, conversa in enumerate(self.conversas_interceptadas, 1):
                timestamp_str = conversa['timestamp'].strftime('%H:%M:%S.%f')[:-3]
                f.write(f"[{timestamp_str}] {conversa.get('agente', 'N/A')}\n")
                f.write(f"Ação: {conversa.get('acao', 'N/A')}\n")
                f.write(f"Conteúdo: {conversa.get('conteudo', 'N/A')}\n")
                f.write("-" * 30 + "\n\n")
        
        return caminho_saida


class InterceptadorCrewAI:
    """
    🎯 Interceptador específico para CrewAI
    
    Monkey-patch para capturar automaticamente todas as comunicações
    """
    
    def __init__(self, espiao: EspionDigital):
        self.espiao = espiao
        self.buffer_original = io.StringIO()
        
    def __enter__(self):
        self.espiao.iniciar_grampo()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.espiao.finalizar_grampo()
        
    def capturar_stdout(self):
        """Captura o stdout para interceptar logs do CrewAI"""
        captured_output = io.StringIO()
        
        class TeeOutput:
            def __init__(self, original, captured, espiao):
                self.original = original
                self.captured = captured
                self.espiao = espiao
                
            def write(self, text):
                self.original.write(text)
                self.captured.write(text)
                
                # Processa em tempo real
                if text.strip():
                    self.espiao.processar_log_crewai(text)
                    
            def flush(self):
                self.original.flush()
                self.captured.flush()
                
        sys.stdout = TeeOutput(sys.stdout, captured_output, self.espiao)
        return captured_output


# Função utilitária para uso fácil
def criar_espiao_instaprice() -> EspionDigital:
    """
    🕵️ Factory function para criar um espião dos agentes Instaprice
    
    Returns:
        Instância configurada do EspionDigital
    """
    return EspionDigital()


def interceptar_conversas_instaprice(funcao_execucao, *args, **kwargs) -> tuple:
    """
    🎧 Decorator/wrapper para interceptar conversas durante execução do Instaprice
    
    Args:
        funcao_execucao: Função que executa o sistema Instaprice
        *args, **kwargs: Argumentos para a função
        
    Returns:
        Tuple com (resultado_execucao, caminho_pdf_gerado)
    """
    espiao = criar_espiao_instaprice()
    
    # Buffer para capturar TUDO que aparece no terminal
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    class InterceptorCompleto:
        def __init__(self, original_stream, espiao):
            self.original = original_stream
            self.espiao = espiao
            self.buffer_completo = ""
            self.agente_atual = "AGENTE_DESCONHECIDO"
            self.capturando_secao = False
            self.tipo_secao = ""
            self.buffer_secao = ""
            
        def write(self, text):
            # Sempre escreve na saída original
            self.original.write(text)
            
            # Acumula no buffer completo
            self.buffer_completo += text
            captured_output.write(text)
            
            # Processa o texto para identificar as conversas dos agentes
            self.processar_texto_completo(text)
                        
        def processar_texto_completo(self, texto):
            """Processa o texto completo para capturar as conversas exatas dos agentes"""
            
            # Identifica início de novo agente
            if "# Agent:" in texto:
                # Salva seção anterior se existir
                if self.buffer_secao.strip():
                    self.espiao.capturar_conversa_agente(
                        self.agente_atual, 
                        self.tipo_secao, 
                        self.buffer_secao.strip()
                    )
                
                # Extrai nome do agente
                lines = texto.split('\n')
                for line in lines:
                    if "# Agent:" in line:
                        self.agente_atual = line.replace("# Agent:", "").strip()
                        break
                        
                self.buffer_secao = texto
                self.tipo_secao = "AGENT_IDENTIFICATION"
                self.capturando_secao = True
                return
            
            # Identifica seções específicas
            secoes_importantes = {
                "## Task:": "TASK_ASSIGNMENT",
                "## Thought:": "AGENT_THINKING", 
                "## Using tool:": "TOOL_USAGE",
                "## Tool Input:": "TOOL_INPUT",
                "## Tool Output:": "TOOL_OUTPUT",
                "## Final Answer:": "FINAL_ANSWER"
            }
            
            for marcador, tipo in secoes_importantes.items():
                if marcador in texto:
                    # Salva seção anterior
                    if self.buffer_secao.strip() and self.tipo_secao:
                        self.espiao.capturar_conversa_agente(
                            self.agente_atual,
                            self.tipo_secao,
                            self.buffer_secao.strip()
                        )
                    
                    # Inicia nova seção
                    self.tipo_secao = tipo
                    self.buffer_secao = texto
                    self.capturando_secao = True
                    return
            
            # Continua acumulando na seção atual
            if self.capturando_secao:
                self.buffer_secao += texto
                
                # Se encontrar próxima seção ou agente, finaliza a atual
                if any(marcador in texto for marcador in secoes_importantes.keys()) or "# Agent:" in texto:
                    # Não processa aqui - será processado na próxima chamada
                    pass
                
        def flush(self):
            # Salva última seção ao finalizar
            if self.buffer_secao.strip() and self.tipo_secao:
                self.espiao.capturar_conversa_agente(
                    self.agente_atual,
                    self.tipo_secao, 
                    self.buffer_secao.strip()
                )
            self.original.flush()
    
    try:
        espiao.iniciar_grampo()
        
        # Redireciona stdout para interceptar TUDO
        interceptor = InterceptorCompleto(original_stdout, espiao)
        sys.stdout = interceptor
        sys.stderr = InterceptorCompleto(original_stderr, espiao)
        
        # Executa a função e captura TODA a saída
        resultado = funcao_execucao(*args, **kwargs)
        
        # Força o flush final para capturar última seção
        interceptor.flush()
        
        # Processa todo o output capturado com regex avançado
        output_completo = captured_output.getvalue()
        espiao.processar_conversas_completas(output_completo)
        
        espiao.finalizar_grampo()
        
    finally:
        # Restaura streams originais
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
    # Gera o PDF com as conversas completas
    pdf_path = espiao.gerar_relatorio_pdf()
    
    return resultado, pdf_path