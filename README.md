
# Murli Q&A App

A Gradio-based question-answering app for daily Murli articles that uses:

- **Ollama** for local LLM inference (Qwen2.5)
- **LangChain + Chroma** for document embeddings and retrieval
- Auto-cache with daily Murli embeddings and automatic deletion after 3 days
- Runs locally via Python or containerized with Docker Compose

---

## Features

- Fetches daily Murli article and creates persistent embeddings  
- Deletes embeddings older than 3 days automatically  
- Uses Ollama's Qwen2.5 model for contextual question answering  
- Retrieval limited to top 2 chunks for faster responses  
- Gradio web UI for interactive Q&A  

---

## Prerequisites

- Python 3.11+  
- Ollama installed locally or running via Docker  
- Docker & Docker Compose (optional, for containerized setup)  
- Git (optional)  

---

## Setup Guide

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/murli-qa.git
cd murli-qa/bababot
```

---

### 2. Python Environment Setup

Create and activate a virtual environment:

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:
```powershell
python -m venv venv
.env\Scriptsctivate
```

Install dependencies:
```bash
pip install --upgrade pip
pip install gradio ollama langchain langchain-community chromadb
```

Run the app:
```bash
python app.py
```

Access the UI at the URL shown in the console (usually http://127.0.0.1:7860).

---

### 3. Installing & Running Ollama Locally

Download Ollama from [https://ollama.com/download](https://ollama.com/download).  

Start Ollama server:
```bash
ollama serve
```

Pull required models:
```bash
ollama pull qwen2.5:0.5b
ollama pull nomic-embed-text
```

Keep Ollama running while using the app.

---

### 4. Using Ollama with Docker Compose

Create `docker-compose.yml` with:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped
    entrypoint: >
      /bin/bash -c "
        ollama serve &
        sleep 5 &&
        ollama pull qwen2.5:0.5b &&
        ollama pull nomic-embed-text &&
        tail -f /dev/null
      "

volumes:
  ollama-data:
```

Run:
```bash
docker-compose up -d ollama
```

---

### 5. Full Docker Compose (App + Ollama)

Example `docker-compose.yml` for both services:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped
    entrypoint: >
      /bin/bash -c "
        ollama serve &
        sleep 5 &&
        ollama pull qwen2.5:0.5b &&
        ollama pull nomic-embed-text &&
        tail -f /dev/null
      "

  murli-app:
    build: ./murli-app
    depends_on:
      - ollama
    ports:
      - "7860:7860"
    environment:
      - OLLAMA_HOST=http://ollama:11434

volumes:
  ollama-data:
```

Start both:
```bash
docker-compose up -d
```

---

## How it Works

- On launch, the app deletes embeddings older than 3 days from `bababot/db` folder.  
- It fetches today's Murli article from `https://babamurli.com/...`  
- It splits text into chunks, generates embeddings with `nomic-embed-text`, and caches them daily.  
- Retrieval returns top 2 relevant chunks to the Ollama Qwen2.5 LLM to answer questions.  
- Gradio provides the front-end UI.

---

## Customization

- Adjust embedding chunk size in `app.py` (`chunk_size=1000`, `chunk_overlap=200`)  
- Change models by editing the Ollama model names in `app.py`  
- Modify embedding cache duration by changing the days in the deletion loop  
- Change the number of retrieved chunks by modifying `.get_relevant_documents(question, k=2)` (if adding `k=2`)  

---

## Troubleshooting

- **Connection refused:** Make sure Ollama is running and listening on port 11434  
- **Module errors:** Verify virtual environment is activated and dependencies installed  
- **Slow responses:** Use smaller embedding models, reduce retrieval chunk number, keep Ollama warm  
- **Docker errors:** Check permissions and Docker daemon status  

---

## Useful Commands

Stop containers:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

Restart Ollama:
```bash
docker-compose restart ollama
```

---

## License

MIT License

---

## Contact

For questions or issues, open an issue or contact: your-email@example.com

---

Thank you for using Murli Q&A! 🙏
