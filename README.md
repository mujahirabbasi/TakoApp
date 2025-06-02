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

- Python 3.8+
- MySQL Server
- [Ollama](https://ollama.ai/) installed and running
- Git

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/takoapp.git
   cd takoapp
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with:
   ```
   DATABASE_URL=mysql://user:password@localhost/takoapp
   SECRET_KEY=your-secret-key
   ```

5. **Initialize the database**
   ```bash
   python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Start Ollama**
   - Install Ollama from https://ollama.ai/download
   - Start the Ollama service
   - Pull the llama2 model: `ollama pull llama2`

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

## Automated Environment Setup (Windows Only)

This project provides a `setup.py` script to automate the environment setup process for Windows users. The script will:
- Set up a Python virtual environment
- Install all required dependencies
- Guide you through installing MySQL and MySQL Workbench
- Guide you through installing Ollama and pulling the llama2 model
- Create the application database
- Generate a `.env` file with the correct database connection string
- Verify the setup

### How to use the setup script

1. Make sure you have Python 3.10.16 installed on your system.
2. Open a terminal (Command Prompt or PowerShell) in the project root directory.
3. Run the setup script:
   ```sh
   python setup.py
   ```
4. Follow the on-screen instructions to complete the setup process.

After the setup is complete, activate the virtual environment and start the application as described in the main instructions above.