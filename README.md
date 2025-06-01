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