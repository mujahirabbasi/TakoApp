# 🤖 TakoApp - AI-Powered Knowledge Base Chat Application

TakoApp is a sophisticated web application that combines FastAPI, LangChain, and Ollama to create an intelligent chat interface for querying internal documentation. The system uses local LLM embeddings, semantic retrieval, and web search capabilities to provide accurate and context-aware responses.

## 🌟 Features

- **Intelligent Document Querying**: Query markdown-based documentation using natural language
- **Local LLM Integration**: Uses `llama2` via Ollama for local LLM responses
- **Semantic Search**: Embedding-powered document retrieval using ChromaDB
- **Smart Routing**: Intelligent routing between document answers, web search, and general LLM responses
- **User Authentication**: Secure login and registration system
- **Conversation Management**: Save and manage chat history
- **Modern UI**: Clean and responsive web interface
- **Debug Tools**: Admin tools to inspect document chunks and matches

## 📚 Document Categories

The system is designed to handle queries about:

1. **HR Manual**
   - Workplace policies
   - Working hours
   - Leaves and holidays
   - Code of conduct
   - Employee rights and responsibilities

2. **Labor Rules**
   - Legal labor obligations
   - Safety regulations
   - Employee protections
   - Statutory benefits
   - Employment law

3. **Product Usage Manual**
   - Technical specifications
   - Hardware setup
   - Board components
   - Interface documentation
   - Operating systems

## 🏗️ System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  FastAPI Server │────▶│  LangChain      │────▶│  Ollama LLM     │
│                 │     │  Agent          │     │                 │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  MySQL Database │     │  ChromaDB       │
│                 │     │  Vector Store   │
└─────────────────┘     └─────────────────┘
```

### Component Interaction Flow

1. **User Request Flow**:
   ```
   User Request → FastAPI → Authentication → LangChain Agent → Response
   ```

2. **Document Processing Flow**:
   ```
   Markdown Docs → Text Splitter → Embeddings → ChromaDB Storage
   ```

3. **Query Processing Flow**:
   ```
   User Query → Semantic Search → Document Retrieval → LLM Processing → Response
   ```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    conversation_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    sources JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### Entity Relationship Diagram
```
┌──────────┐       ┌───────────────┐       ┌──────────┐
│  Users   │       │ Conversations │       │ Messages │
├──────────┤       ├───────────────┤       ├──────────┤
│ id       │       │ user_id       │       │ conv_id  │
│ username │       │ title         │       │ content  │
│ email    │◄──────┤ created_at    │       │ role     │
│ password │       │ updated_at    │       │ sources  │
│ created  │       │               │       │ created  │
└──────────┘       └───────────────┘       │ updated  │
                                           └──────────┘
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: LangChain, Ollama (llama2)
- **Database**: MySQL
- **Vector Store**: ChromaDB
- **Authentication**: Session-based auth with bcrypt
- **Search**: DuckDuckGo API for web search

## 📋 Prerequisites

- Python 3.10.16
- MySQL Server
- [Ollama](https://ollama.ai/) installed and running
- Git

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/takoapp.git
   cd takoapp
   ```

2. **Create and activate a conda virtual environment (Python 3.10.16)**
   ```bash
   conda create -n takoapp_env python=3.10.16
   conda activate takoapp_env
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and install MySQL Server and MySQL Workbench**
   - Download MySQL Server: https://dev.mysql.com/downloads/installer/
   - Download MySQL Workbench: https://dev.mysql.com/downloads/workbench/
   - Install both using the installers and make sure MySQL Server is running.

5. **.env file**
   - A pre-configured `.env` file is already included in the repository. You do not need to create or modify it. The application will use this file for database and other configuration settings.

6. **Start Ollama**
   - Download and install Ollama from https://ollama.ai/download
   - Start the Ollama service
   - Pull the llama2 model:
     ```bash
     ollama pull llama2
     ```

## 🏃‍♂️ Running the Application

1. **Start the server**
   ```bash
   python run.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 📁 Project Structure

```
takoapp/
├── agent/                 # AI agent implementation
│   ├── docs/             # Documentation files
│   ├── utils/            # Utility functions
│   └── kb_agent.py       # Knowledge base agent
├── app/                  # FastAPI application
│   ├── auth/            # Authentication
│   ├── models/          # Database models
│   ├── routers/         # API routes
│   ├── schemas/         # Pydantic schemas
│   └── main.py          # Application entry point
├── static/              # Static files
├── templates/           # HTML templates
├── db/                  # Database files
├── requirements.txt     # Python dependencies
└── run.py              # Application runner
```

## 🔧 Configuration

- **Database**: Configure MySQL connection in `.env`
- **Ollama**: Ensure Ollama is running and llama2 model is available
- **Documentation**: Place markdown files in `agent/docs/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [Ollama](https://ollama.ai/)
- [ChromaDB](https://www.trychroma.com/)

## Inspecting Document Chunks

The project includes a script, `agent/inspect_chunks.py`, which allows you to inspect how your documentation is split into chunks and stored in the Chroma vector database. This is useful for debugging, understanding retrieval, and ensuring your documents are chunked as expected.

### How to use the chunk inspection script

- To inspect all chunks:
  ```sh
  python agent/inspect_chunks.py
  ```
- To inspect chunks for a specific document (e.g., `hr_manual.md`):
  ```sh
  python agent/inspect_chunks.py --source hr_manual.md
  ```
- Inspection reports are saved in the `agent/chunks_inspection/` folder.

## Note on Environment File

A pre-configured `.env` file is included in the repository for your convenience. You do **not** need to create or generate a `.env` file manually; simply use the one provided. This allows reviewers and users to run the application with minimal setup effort.