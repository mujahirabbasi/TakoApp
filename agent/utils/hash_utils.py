"""
Utility functions for document hash computation and management.
"""

import os
import hashlib
from langchain.schema import Document

def compute_document_hash(documents):
    """Compute a hash of document contents to check if they've changed."""
    content = "".join(doc.page_content for doc in documents)
    print(f"[DEBUG] Computing hash for content length: {len(content)}")
    print(f"[DEBUG] First 100 chars of content: {content[:100]}")
    hash_value = hashlib.md5(content.encode()).hexdigest()
    print(f"[DEBUG] Computed hash: {hash_value}")
    return hash_value

def load_document_hash():
    """Load the saved document hash if it exists."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    try:
        with open(os.path.join(db_dir, "document_hash.txt"), "r") as f:
            hash_value = f.read().strip()
            print(f"[DEBUG] Loaded hash from file: {hash_value}")
            return hash_value
    except FileNotFoundError:
        print("[DEBUG] No hash file found")
        return None

def save_document_hash(hash_value):
    """Save the document hash."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db")
    db_dir = os.path.abspath(db_dir)
    os.makedirs(db_dir, exist_ok=True)
    print(f"[DEBUG] Saving hash to file: {hash_value}")
    with open(os.path.join(db_dir, "document_hash.txt"), "w") as f:
        f.write(hash_value) 