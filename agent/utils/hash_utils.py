"""
Utility functions for document hash computation and management.
"""

import os
import hashlib
from langchain.schema import Document

def compute_document_hash(documents):
    """Compute a hash of document contents to check if they've changed."""
    content = "".join(doc.page_content for doc in documents)
    return hashlib.md5(content.encode()).hexdigest()

def load_document_hash():
    """Load the saved document hash if it exists."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    try:
        with open(os.path.join(db_dir, "document_hash.txt"), "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_document_hash(hash_value):
    """Save the document hash."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    os.makedirs(db_dir, exist_ok=True)
    with open(os.path.join(db_dir, "document_hash.txt"), "w") as f:
        f.write(hash_value) 