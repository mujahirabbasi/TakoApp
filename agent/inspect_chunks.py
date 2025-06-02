"""
Script to inspect and analyze chunks stored in the Chroma database.
"""

import os
import time
from tabulate import tabulate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from utils.hash_utils import load_document_hash

def inspect_chunks(show_content=True, show_metadata=True, source_filter=None):
    """Inspect chunks stored in the Chroma database and save to file."""
    print("\n🔍 Inspecting Chroma database...")
    
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
    db_dir = os.path.abspath(db_dir)
    # Check if database exists
    if not os.path.exists(os.path.join(db_dir, "chroma.sqlite3")):
        print(f"❌ No database found at {os.path.join(db_dir, 'chroma.sqlite3')}")
        return
    
    # Load the saved hash
    saved_hash = load_document_hash()
    if saved_hash:
        print(f"📝 Document hash: {saved_hash}")
    
    # Initialize vectorstore
    embedding = OllamaEmbeddings(model="llama2")
    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=embedding
    )
    
    # Get all documents
    results = vectorstore.get()
    
    if not results or not results['documents']:
        print("❌ No documents found in the database")
        return
    
    # Print raw results for debugging
    print("\nRaw database contents:")
    print(f"Number of documents: {len(results['documents'])}")
    print(f"Number of metadatas: {len(results['metadatas'])}")
    print("\nAvailable sources in database:")
    sources = set(metadata.get('source') for metadata in results['metadatas'])
    for source in sources:
        print(f"- {source}")
    
    # Prepare data for display
    chunks = []
    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
        # Apply source filter if specified
        if source_filter and metadata.get('source') != source_filter:
            continue
            
        chunk_info = {
            'Chunk #': i + 1,
            'Source': metadata.get('source', 'Unknown'),
            'Type': metadata.get('chunk_type', 'Unknown'),
            'Length': len(doc)
        }
        
        if show_metadata:
            # Add all metadata fields
            for key, value in metadata.items():
                if key not in ['source', 'chunk_type']:
                    chunk_info[key] = value
        
        if show_content:
            # Add first 100 chars of content
            chunk_info['Content Preview'] = doc[:100] + "..." if len(doc) > 100 else doc
        
        chunks.append(chunk_info)
    
    # Check if we found any chunks
    if not chunks:
        if source_filter:
            print(f"❌ No chunks found for source: {source_filter}")
            print("\nAvailable sources in database:")
            for source in sources:
                print(f"- {source}")
        else:
            print("❌ No chunks found in the database")
        return
    
    # Create output directory if it doesn't exist
    inspection_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks_inspection")
    os.makedirs(inspection_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"chunks_{timestamp}.txt"
    if source_filter:
        filename = f"chunks_{source_filter}_{timestamp}.txt"
    filename = os.path.join(inspection_dir, filename)
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("🔍 Chroma Database Inspection Report\n")
        f.write("=" * 50 + "\n\n")
        
        if saved_hash:
            f.write(f"Document hash: {saved_hash}\n\n")
        
        f.write(f"Found {len(chunks)} chunks\n")
        if source_filter:
            f.write(f"Filtered by source: {source_filter}\n")
        
        # Write table
        headers = list(chunks[0].keys())
        rows = [[chunk[header] for header in headers] for chunk in chunks]
        f.write("\n" + tabulate(rows, headers=headers, tablefmt="grid"))
        
        # Write statistics
        f.write("\n\n📈 Statistics:\n")
        sources = {}
        types = {}
        for chunk in chunks:
            source = chunk['Source']
            chunk_type = chunk['Type']
            sources[source] = sources.get(source, 0) + 1
            types[chunk_type] = types.get(chunk_type, 0) + 1
        
        f.write("\nChunks by source:\n")
        for source, count in sources.items():
            f.write(f"- {source}: {count} chunks\n")
        
        f.write("\nChunks by type:\n")
        for type_, count in types.items():
            f.write(f"- {type_}: {count} chunks\n")
    
    print(f"\n✅ Inspection report saved to: {filename}")
    
    # Also show a preview in the terminal
    print(f"\n📊 Found {len(chunks)} chunks")
    if source_filter:
        print(f"Filtered by source: {source_filter}")
    
    # Show first 5 chunks in terminal as preview
    preview_chunks = chunks[:5]
    headers = list(preview_chunks[0].keys())
    rows = [[chunk[header] for header in headers] for chunk in preview_chunks]
    print("\nPreview of first 5 chunks:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\n... and {len(chunks) - 5} more chunks (see full report in {filename})")

def main():
    """Main function to handle command line arguments and run inspection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inspect chunks in the Chroma database')
    parser.add_argument('--source', help='Filter chunks by source file')
    parser.add_argument('--no-content', action='store_true', help='Hide content preview')
    parser.add_argument('--no-metadata', action='store_true', help='Hide metadata')
    
    args = parser.parse_args()
    
    inspect_chunks(
        show_content=not args.no_content,
        show_metadata=not args.no_metadata,
        source_filter=args.source
    )

if __name__ == "__main__":
    main() 