# 📚 Knowledge Base Q&A System (LangChain + Ollama + FastAPI)

This project is an AI-powered assistant that answers questions based on internal markdown documentation. It supports HR policies, labor laws, and product usage manuals by combining local LLM embeddings, semantic retrieval, and web search fallback.

## 🚀 Features

- ✅ Query markdown-based documents with natural language
- 🤖 Uses `llama2` via Ollama for local LLM responses
- 🧠 Embedding-powered document retrieval using ChromaDB
- 🔀 Intelligent routing between document answers, web search, and general LLM
- 🔧 Admin debug tool to inspect which chunks match a query
- 🌐 FastAPI backend ready for web integration

## 🗂 Document Categories

1. **HR Manual**
2. **Labor Rules**
3. **Product Usage Manual**

These categories are inferred based on keywords and used to guide routing logic.

## 📦 Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/yourusername/kb-qa-agent.git
cd kb-qa-agent
pip install -r requirements.txt
```

### 2. Start Ollama and Download Model

Install [Ollama](https://ollama.ai/) and make sure it's running:

```bash
ollama run llama2
```

### 3. Prepare Your Markdown Files

Place your documentation files (e.g., `hr_manual.md`, `labor_rules.md`, `product_usage_manual.md`) inside the `/docs` folder.

### 4. Run the Knowledge Agent

```bash
python kb_agent.py
```

You'll see a prompt where you can ask questions directly.

## 🧪 Example Queries

- "What are the rules relating to trade union recognition?"
- "What is the parental leave policy?"
- "How do I connect a monitor to the ROCK960 board?"

## ⚙️ Architecture

```
LangChain + Ollama + Chroma
        |
    Retriever + LLM + Web Tool
        |
  Custom Router & FastAPI Backend
```

## 📊 Evaluation Metrics

- 🔍 **Chunk Match Rate** — % of queries that retrieve correct section
- 🧠 **Answer Accuracy** — qualitative check against known answers
- ⏱ **Response Time** — <1 sec ideal for retrieval

## 🛡 Privacy & Data Handling

- All processing is local via Ollama — no data leaves the machine
- Documents are embedded and stored using hash-based versioning
- No external APIs are called unless web search is explicitly invoked

## 📝 Future Improvements

- Web UI using Streamlit or React
- LangGraph support for advanced agent control
- User feedback collection on each answer


## 📄 License

This project is licensed under the MIT License.