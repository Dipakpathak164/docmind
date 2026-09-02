#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path

import hashlib
from datetime import datetime

# LlamaIndex Imports
from llama_index.core import SimpleDirectoryReader, Document, StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

import config

def compute_hash(content: str) -> str:
    """Compute SHA256 hash for document content deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def get_chroma_client_and_collection(collection_name: str = None):
    """Utility to retrieve persistent Chroma client and specified collection."""
    name = collection_name or config.COLLECTION_NAME
    db = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    collection = db.get_or_create_collection(name)
    return db, collection

def get_indexed_documents(collection_name: str = None) -> list[dict]:
    """
    Retrieve a summarized catalog of all documents indexed in the vector database.
    Returns a list of dicts with keys: source, file_name, file_hash, chunk_count, indexed_at.
    """
    try:
        _, collection = get_chroma_client_and_collection(collection_name)
        data = collection.get(include=["metadatas"])
        metadatas = data.get("metadatas", [])
        
        if not metadatas:
            return []
            
        doc_map = {}
        for meta in metadatas:
            if not meta:
                continue
            src = meta.get("source") or meta.get("file_name") or "Unknown Source"
            file_name = meta.get("file_name") or src
            file_hash = meta.get("file_hash", "")
            indexed_at = meta.get("indexed_at", "N/A")
            
            if src not in doc_map:
                doc_map[src] = {
                    "source": src,
                    "file_name": file_name,
                    "file_hash": file_hash,
                    "chunk_count": 0,
                    "indexed_at": indexed_at
                }
            doc_map[src]["chunk_count"] += 1
            
        return list(doc_map.values())
    except Exception as e:
        print(f"Error fetching indexed documents: {e}", file=sys.stderr)
        return []

def delete_document(source: str, collection_name: str = None) -> int:
    """
    Delete all vector nodes belonging to a specific file or URL source.
    Returns the number of deleted chunks.
    """
    try:
        _, collection = get_chroma_client_and_collection(collection_name)
        data = collection.get(include=["metadatas"])
        ids_to_delete = []
        
        for idx, meta in zip(data.get("ids", []), data.get("metadatas", [])):
            if meta and (meta.get("source") == source or meta.get("file_name") == source or meta.get("file_hash") == source):
                ids_to_delete.append(idx)
                
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            return len(ids_to_delete)
        return 0
    except Exception as e:
        print(f"Error deleting document '{source}': {e}", file=sys.stderr)
        return 0

def clear_knowledge_base(collection_name: str = None) -> bool:
    """Clear all documents and vectors from the specified Chroma collection."""
    try:
        db, _ = get_chroma_client_and_collection(collection_name)
        target_name = collection_name or config.COLLECTION_NAME
        db.delete_collection(target_name)
        db.get_or_create_collection(target_name)
        return True
    except Exception as e:
        print(f"Error clearing knowledge base: {e}", file=sys.stderr)
        return False

def load_url(url: str) -> list[Document]:
    """Fetch text content from a URL and return a LlamaIndex Document with metadata."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch content from URL '{url}': {e}")

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script, style, and navigation tags
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        text = soup.get_text(separator=" ")
        
        # Clean up text whitespace
        cleaned_text = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )
        
        if not cleaned_text:
            raise ValueError("No text content could be extracted from the URL.")
            
        file_hash = compute_hash(cleaned_text)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return [Document(
            text=cleaned_text,
            metadata={
                "source": url,
                "file_name": title,
                "file_hash": file_hash,
                "indexed_at": now_str,
                "file_size": len(cleaned_text.encode("utf-8"))
            }
        )]
    except Exception as e:
        raise ValueError(f"Error parsing content from URL '{url}': {e}")

def ingest_source(source: str, force_reindex: bool = False) -> tuple[int, int]:
    """Ingest documents from a file, directory, or URL, chunk them, embed, and store in Chroma with deduplication."""
    # Configure LlamaIndex Embeddings and Node Parser
    if config.OPENAI_API_KEY:
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=config.OPENAI_API_KEY
        )
    elif config.GEMINI_API_KEY:
        Settings.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=config.GEMINI_API_KEY
        )

    # Check if source is a URL or local path
    is_url = source.startswith(("http://", "https://"))
    documents = []
    
    if is_url:
        documents = load_url(source)
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Source path '{source}' does not exist.")
            
        if path.is_file():
            reader = SimpleDirectoryReader(input_files=[str(path)])
            documents = reader.load_data()
        elif path.is_dir():
            reader = SimpleDirectoryReader(input_dir=str(path))
            documents = reader.load_data()
        else:
            raise ValueError(f"Source path '{source}' is neither a file nor a directory.")
            
    if not documents:
        raise ValueError(f"No documents or text could be loaded from source '{source}'.")

    # Deduplication check
    db, chroma_collection = get_chroma_client_and_collection()
    existing_hashes = set()
    try:
        data = chroma_collection.get(include=["metadatas"])
        for meta in data.get("metadatas", []):
            if meta and "file_hash" in meta:
                existing_hashes.add(meta["file_hash"])
    except Exception:
        pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_documents = []
    for doc in documents:
        doc_hash = compute_hash(doc.text)
        if not force_reindex and doc_hash in existing_hashes:
            print(f"Skipping document (already indexed with hash {doc_hash[:8]}): {doc.metadata.get('file_name', source)}")
            continue
            
        doc.metadata["file_hash"] = doc_hash
        doc.metadata["indexed_at"] = now_str
        if "file_name" not in doc.metadata:
            doc.metadata["file_name"] = Path(source).name if not is_url else source
        if "source" not in doc.metadata:
            doc.metadata["source"] = source
        new_documents.append(doc)

    if not new_documents:
        if not force_reindex:
            return 0, len(documents)
        new_documents = documents

    # Split into chunks (nodes)
    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    nodes = splitter.get_nodes_from_documents(new_documents)
    
    if not nodes:
        raise ValueError("Document text was too short or empty, no chunks generated.")

    # Ensure all nodes carry full metadata
    for node in nodes:
        for k, v in new_documents[0].metadata.items():
            if k not in node.metadata:
                node.metadata[k] = v

    # Index the nodes
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=Settings.embed_model
    )
    
    return len(nodes), len(new_documents)

def main():
    parser = argparse.ArgumentParser(description="DocMind Ingestion CLI Script")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a file, directory, or a URL to index into the vector store."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing even if document hash already exists in vector DB."
    )
    args = parser.parse_args()
    
    try:
        print(f"Indexing source: {args.source}...")
        num_chunks, num_docs = ingest_source(args.source, force_reindex=args.force)
        if num_chunks == 0:
            print("All documents in source are already indexed. Use --force to re-index.")
        else:
            print(f"Indexed {num_chunks} chunks from {num_docs} documents")
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

