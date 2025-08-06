import datetime
import os
import shutil
import gradio as gr
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Base directory for embeddings
base_db_dir = "bababot/db"
os.makedirs(base_db_dir, exist_ok=True)

# Delete old embeddings (older than 3 days)
now = datetime.datetime.now()
for folder in os.listdir(base_db_dir):
    folder_path = os.path.join(base_db_dir, folder)
    try:
        folder_date = datetime.datetime.strptime(folder, "%d.%m.%y")
        if (now - folder_date).days > 3:
            shutil.rmtree(folder_path)
            print(f"Deleted old embeddings: {folder}")
    except ValueError:
        pass  # Ignore folders that don't match date format

# Generate today's Murli URL
today = datetime.date.today()
date_str = today.strftime("%d.%m.%y")
base_url = "https://babamurli.com/01.%20Daily%20Murli/02.%20English/01.%20Eng%20Murli%20-%20Htm/"
filename = f"{date_str}-E.htm"
url = base_url + filename

# Embedding model (smaller & faster)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Today's persistence directory
persist_dir = os.path.join(base_db_dir, date_str)
os.makedirs(persist_dir, exist_ok=True)

# Load or create embeddings
if os.path.exists(os.path.join(persist_dir, "index")):
    print(f"Loading cached embeddings for {date_str}...")
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
else:
    print(f"Fetching and embedding Murli for {date_str}...")
    loader = WebBaseLoader(url)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    vectorstore.persist()

retriever = vectorstore.as_retriever()

# Ollama call
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(
        model='hf.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q2_K',
        messages=[{'role': 'user', 'content': formatted_prompt}]
    )
    return response['message']['content']

# Retrieval + LLM with top 2 docs only
def rag_chain(question):
    retrieved_docs = retriever.get_relevant_documents(question)
    top_docs = retrieved_docs[:2]  # limit to 2 documents
    formatted_context = "\n\n".join(doc.page_content for doc in top_docs)
    return ollama_llm(question, formatted_context)

# Gradio app
def get_important_facts(question):
    return rag_chain(question)

iface = gr.Interface(
    fn=get_important_facts,
    inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
    outputs="text",
    title=f"Murli Q&A - {date_str}",
    description=f"Ask questions about the Murli article for {date_str}"
)

iface.launch()
