"""
Utility functions for computing and storing document embeddings.
"""
import os
import re
from pathlib import Path
from langchain.schema import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from .hash_utils import compute_document_hash, load_document_hash, save_document_hash

def split_markdown_sections(text: str, filename: str) -> list[Document]:
    """Split markdown by uniform ## headers into Document chunks."""
    pattern = r"(##\s+.+?)(?=\n##\s+|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)

    documents = []
    for match in matches:
        header_line = match.splitlines()[0].strip()
        section_title = header_line.lstrip('#').strip()
        content = match.strip()
        doc = Document(
            page_content=content,
            metadata={
                "source": filename,
                "header": section_title
            }
        )
        documents.append(doc)
    return documents

def compute_and_store_embeddings(embedding_model="llama2"):
    """Compute embeddings from normalized markdown files and store them."""
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs")
    docs_dir = os.path.abspath(docs_dir)
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)

    markdown_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    all_docs = []

    for doc_file in markdown_files:
        file_path = os.path.join(docs_dir, doc_file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = split_markdown_sections(text, doc_file)
        all_docs.extend(chunks)

    if not all_docs:
        raise ValueError("No documents loaded.")

    os.makedirs(db_dir, exist_ok=True)

    current_hash = compute_document_hash(all_docs)
    saved_hash = load_document_hash()

    embedding = OllamaEmbeddings(model=embedding_model)
    vectorstore = Chroma.from_documents(
        all_docs,
        embedding,
        persist_directory=db_dir
    )

    save_document_hash(current_hash)

    return vectorstore

if __name__ == "__main__":
    compute_and_store_embeddings()
