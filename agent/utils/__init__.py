"""
Utility functions for the knowledge base agent.
"""

from .compute_embeddings import compute_and_store_embeddings
from .ollama_utils import get_ollama_path, check_ollama_availability, wait_for_ollama, check_and_pull_model
from .hash_utils import compute_document_hash, load_document_hash, save_document_hash

__all__ = [
    'compute_and_store_embeddings',
    'get_ollama_path',
    'check_ollama_availability',
    'wait_for_ollama',
    'check_and_pull_model',
    'compute_document_hash',
    'load_document_hash',
    'save_document_hash'
] 