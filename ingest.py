#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# LlamaIndex Imports
from llama_index.core import SimpleDirectoryReader, Document, StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

import config

def load_url(url: str) -> list[Document]:
    """Fetch text content from a URL and return a LlamaIndex Document."""
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
            
        return [Document(text=cleaned_text, metadata={"source": url, "file_name": title})]
    except Exception as e:
        raise ValueError(f"Error parsing content from URL '{url}': {e}")

def ingest_source(source: str) -> tuple[int, int]:
    """Ingest documents from a file, directory, or URL, chunk them, embed, and store in Chroma."""
    # Configure LlamaIndex Embeddings and Node Parser
    if config.OPENAI_API_KEY:
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=config.OPENAI_API_KEY
        )
    elif config.GEMINI_API_KEY:
        Settings.embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
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

    # Split into chunks (nodes)
    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    nodes = splitter.get_nodes_from_documents(documents)
    
    if not nodes:
        raise ValueError("Document text was too short or empty, no chunks generated.")

    # Initialize Chroma client and store
    db = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    chroma_collection = db.get_or_create_collection(config.COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Index the nodes
    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=Settings.embed_model
    )
    
    return len(nodes), len(documents)

def main():
    parser = argparse.ArgumentParser(description="DocMind Ingestion CLI Script")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a file, directory, or a URL to index into the vector store."
    )
    args = parser.parse_args()
    
    try:
        print(f"Indexing source: {args.source}...")
        num_chunks, num_docs = ingest_source(args.source)
        print(f"Indexed {num_chunks} chunks from {num_docs} documents")
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
