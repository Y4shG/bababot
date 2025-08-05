import os
import datetime
import gradio as gr
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Set ollama base URL from env var, fallback to localhost (for local runs)
ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama.base_url = ollama_base_url

# 1. Generate date string in format "dd.mm.yy"
today = datetime.date.today()
date_str = today.strftime("%d.%m.%y")  # e.g. "05.08.25"

# 2. Construct the URL automagically (ooh ahh) if this doesn't work its most likely due to that babamurli isn't using the same url instruction, the current date format is listed below.
base_url = "https://babamurli.com/01.%20Daily%20Murli/02.%20English/01.%20Eng%20Murli%20-%20Htm/"
filename = f"{date_str}-E.htm"
url = base_url + filename

# 3. Load and process the URL
loader = WebBaseLoader(url)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

retriever = vectorstore.as_retriever()

# 4. Define Ollama call
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(model='qwen2.5:0.5b', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

# 5. RAG chain function
def rag_chain(question):
    retrieved_docs = retriever.get_relevant_documents(question)
    formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return ollama_llm(question, formatted_context)

# 6. Gradio interface function
def get_important_facts(question):
    return rag_chain(question)

iface = gr.Interface(
    fn=get_important_facts,
    inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
    outputs="text",
    title=f"RAG with qwen2.5 - {date_str}",
    description=f"Ask questions about the Murli article for {date_str}",
)

iface.launch()
