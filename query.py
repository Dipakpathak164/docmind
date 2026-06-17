import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.gemini import Gemini
from llama_index.core.response_synthesizers import get_response_synthesizer

import config

def answer(question: str) -> dict:
    """
    Retrieves relevant document chunks and queries the LLM to generate an answer.
    
    Args:
        question: The user query string.
        
    Returns:
        dict: A dictionary containing:
            - "answer" (str): LLM response or default message
            - "sources" (list): Chunks used containing text, score, and source name
            - "has_answer" (bool): True if chunks above similarity cutoff exist, else False
    """
    # Configure LlamaIndex LLM and Embeddings globally for query process
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

    if config.ANTHROPIC_API_KEY:
        Settings.llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.ANTHROPIC_API_KEY
        )
    elif config.GEMINI_API_KEY:
        Settings.llm = Gemini(
            model_name="models/gemini-2.5-flash",
            api_key=config.GEMINI_API_KEY
        )



    
    try:
        # Connect to Chroma persistent client
        db = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        
        # Check if collection exists and has elements
        try:
            collections = db.list_collections()
            collection_names = [c.name for c in collections]
            if config.COLLECTION_NAME not in collection_names:
                return {
                    "answer": "I could not find relevant information in the documents.",
                    "sources": [],
                    "has_answer": False
                }
            chroma_collection = db.get_collection(config.COLLECTION_NAME)
        except Exception:
            return {
                "answer": "I could not find relevant information in the documents.",
                "sources": [],
                "has_answer": False
            }
            
        if chroma_collection.count() == 0:
            return {
                "answer": "I could not find relevant information in the documents.",
                "sources": [],
                "has_answer": False
            }

        # Setup Vector Store Index from Chroma
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=Settings.embed_model
        )
        
        # Retrieve candidate nodes
        retriever = index.as_retriever(similarity_top_k=config.TOP_K)
        retrieved_nodes = retriever.retrieve(question)
        
        # Filter nodes above the configured similarity threshold
        filtered_nodes = []
        for node in retrieved_nodes:
            score = node.score if node.score is not None else 0.0
            if score >= config.SIMILARITY_CUTOFF:
                filtered_nodes.append(node)
                
        # If no nodes pass the cutoff, return default answer
        if not filtered_nodes:
            return {
                "answer": "I could not find relevant information in the documents.",
                "sources": [],
                "has_answer": False
            }
            
        # Synthesize answer using LlamaIndex Response Synthesizer
        response_synthesizer = get_response_synthesizer(
            llm=Settings.llm,
            response_mode="compact"
        )
        response = response_synthesizer.synthesize(question, nodes=filtered_nodes)
        answer_text = str(response).strip()
        
        # Form source metadata outputs
        sources = []
        for node in filtered_nodes:
            source_name = node.metadata.get("file_name") or node.metadata.get("source") or "Unknown"
            sources.append({
                "text": node.text[:300],
                "score": float(node.score) if node.score is not None else 0.0,
                "source": str(source_name)
            })
            
        return {
            "answer": answer_text,
            "sources": sources,
            "has_answer": True
        }
        
    except Exception as e:
        return {
            "answer": f"An error occurred during query processing: {str(e)}",
            "sources": [],
            "has_answer": False
        }
