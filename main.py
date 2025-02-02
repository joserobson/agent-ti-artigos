import os
from fpdf import FPDF
from crewai import Agent, Task, Crew
from groq import Groq
from langchain.tools import Tool
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configuração do cliente Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Criar ferramenta para gerar artigo
def generate_article(topic):
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Você é um especialista em desenvolvimento .NET."},
            {"role": "user", "content": f"Escreva um artigo detalhado sobre {topic}."}
        ]
    )
    return response.choices[0].message.content

generate_article_tool = Tool(
    name="generate_article",
    func=generate_article,
    description="Gera um artigo detalhado sobre um tópico específico relacionado a .NET."
)

# Criar ferramenta para revisar texto
def revisar_texto(texto):
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Você é um revisor técnico especializado em .NET."},
            {"role": "user", "content": f"Revise este artigo e melhore a clareza e a estrutura:\n\n{texto}"}
        ]
    )
    return response.choices[0].message.content

revisar_texto_tool = Tool(
    name="revisar_texto",
    func=revisar_texto,
    description="Revise um artigo e melhore sua clareza e estrutura."
)

# Criar ferramenta para salvar como PDF
def salvar_como_pdf(titulo, texto):
    if not os.path.exists("./output"):
        os.makedirs("./output")
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, titulo, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, texto)
    pdf.output(f"./output/{titulo.replace(' ', '_')}.pdf")

salvar_como_pdf_tool = Tool(
    name="salvar_como_pdf",
    func=salvar_como_pdf,
    description="Salva um artigo revisado como um arquivo PDF formatado."
)

# Criando agentes
escritor = Agent(
    role="Escritor de Artigos .NET",
    goal="Criar artigos técnicos detalhados sobre .NET",
    backstory="Um redator experiente que adora explicar conceitos complexos de forma simples e envolvente.",
    tools=[generate_article_tool],
    verbose=True
)

revisor = Agent(
    role="Revisor Técnico",
    goal="Melhorar a clareza e a formatação dos artigos",
    backstory="Especialista em revisar artigos técnicos, garantindo clareza e precisão.",
    tools=[revisar_texto_tool],
    verbose=True
)

formatador = Agent(
    role="Formatador de PDFs",
    goal="Converter artigos revisados em PDFs formatados",
    backstory="Especialista em formatação e criação de documentos PDF bem estruturados.",
    tools=[salvar_como_pdf_tool],
    verbose=True
)

# Definir tarefas
# Definir tarefas com expected_output
tarefa_escrita = Task(
    description="Escrever um artigo sobre .NET",
    expected_output="Um artigo detalhado sobre boas práticas no desenvolvimento .NET.",
    agent=escritor
)

tarefa_revisao = Task(
    description="Revisar o artigo e melhorar a clareza",
    expected_output="O artigo revisado com melhorias na clareza e estrutura.",
    agent=revisor
)

tarefa_formatacao = Task(
    description="Salvar o artigo como PDF",
    expected_output="Um arquivo PDF contendo o artigo revisado e formatado.",
    agent=formatador
)

# Criar equipe (Crew)
crew = Crew(
    agents=[escritor, revisor, formatador],
    tasks=[tarefa_escrita, tarefa_revisao, tarefa_formatacao]
)

# Rodar o fluxo de trabalho
if __name__ == "__main__":
    artigo = generate_article("Boas práticas no desenvolvimento .NET")
    artigo_revisado = revisar_texto(artigo)
    salvar_como_pdf("Boas práticas no desenvolvimento .NET", artigo_revisado)
    print("✅ Artigo gerado e salvo em ./output/")
