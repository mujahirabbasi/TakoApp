"""
Shared components and initialization logic for the application.
"""
from agent.kb_agent import initialize_ollama, initialize_embeddings, create_retriever_tool, create_web_search_tool
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA

# Initialize KB Agent components
try:
    initialize_ollama()
    vectorstore = initialize_embeddings()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    llm = ChatOllama(model="llama2", temperature=0)
    retrieval_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    retriever_tool = create_retriever_tool(retrieval_chain)
    web_search_tool = create_web_search_tool()
    tools = [retriever_tool, web_search_tool]
except Exception as e:
    tools = None
    llm = None
    retriever = None 