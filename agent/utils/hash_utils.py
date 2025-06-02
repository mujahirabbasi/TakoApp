"""
Utility functions for document hash computation and management.
"""

import os
import hashlib

def compute_document_hash(documents):
    """Compute a hash of document contents to check if they've changed."""
    content = "".join(doc.page_content for doc in documents)
    hash_value = hashlib.md5(content.encode()).hexdigest()
    return hash_value

def load_document_hash():
    """Load the saved document hash if it exists."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    try:
        with open(os.path.join(db_dir, "document_hash.txt"), "r") as f:
            hash_value = f.read().strip()
            return hash_value
    except FileNotFoundError:
        return None

def save_document_hash(hash_value):
    """Save the document hash."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    os.makedirs(db_dir, exist_ok=True)
    with open(os.path.join(db_dir, "document_hash.txt"), "w") as f:
        f.write(hash_value) 