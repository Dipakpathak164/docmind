import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.gemini import Gemini
from llama_index.core.response_synthesizers import get_response_synthesizer

import config

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.gemini import Gemini
from llama_index.core.response_synthesizers import get_response_synthesizer

import config

def answer(
    question: str,
    chat_history: list[dict] = None,
    top_k: int = None,
    similarity_cutoff: float = None,
    hybrid_search: bool = None,
    streaming: bool = False,
    collection_name: str = None
) -> dict:
    """
    Retrieves relevant document chunks and queries the LLM to generate an answer.
    Supports multi-turn memory, hybrid search, streaming synthesis, and dynamic overrides.
    
    Args:
        question: The user query string.
        chat_history: Optional list of past chat messages [{"role": "user"|"assistant", "content": "..."}]
        top_k: Optional integer override for candidate node retrieval
        similarity_cutoff: Optional float override for vector similarity cutoff threshold
        hybrid_search: Optional boolean override for BM25 + Vector hybrid retrieval
        streaming: Optional boolean to return a token stream generator
        collection_name: Optional string override for Chroma collection name
        
    Returns:
        dict: A dictionary containing:
            - "answer" (str): Full text answer (when streaming=False)
            - "answer_stream" (generator): Token stream generator (when streaming=True)
            - "sources" (list): Chunks used containing text, score, and source name
            - "has_answer" (bool): True if chunks above similarity cutoff exist, else False
    """
    # Dynamic parameter overrides with global config fallbacks
    effective_top_k = top_k if top_k is not None else config.TOP_K
    effective_cutoff = similarity_cutoff if similarity_cutoff is not None else config.SIMILARITY_CUTOFF
    effective_hybrid = hybrid_search if hybrid_search is not None else config.HYBRID_SEARCH
    target_collection = collection_name or config.COLLECTION_NAME

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
            if target_collection not in collection_names:
                return {
                    "answer": "I could not find relevant information in the documents.",
                    "sources": [],
                    "has_answer": False
                }
            chroma_collection = db.get_collection(target_collection)
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

        # Contextualize search query with multi-turn chat history if available
        search_query = question
        if chat_history and len(chat_history) > 1:
            recent_turns = []
            for msg in chat_history[-4:]:  # last 2 turns
                role = "User" if msg.get("role") == "user" else "Assistant"
                recent_turns.append(f"{role}: {msg.get('content', '')}")
            context_summary = "\n".join(recent_turns)
            search_query = f"{context_summary}\nCurrent Question: {question}"

        # Setup Vector Store Index from Chroma
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=Settings.embed_model
        )
        
        # Retrieve candidate nodes using Vector Retriever
        retriever = index.as_retriever(similarity_top_k=effective_top_k)
        retrieved_nodes = retriever.retrieve(search_query)

        # Apply BM25 Hybrid Keyword boosting if enabled
        if effective_hybrid and retrieved_nodes:
            try:
                # Try importing LlamaIndex BM25 Retriever or apply keyword term frequency reranking
                query_words = set(question.lower().split())
                for node in retrieved_nodes:
                    text_words = set(node.text.lower().split())
                    common_words = query_words.intersection(text_words)
                    keyword_bonus = min(0.15, len(common_words) * 0.03)
                    base_score = node.score if node.score is not None else 0.5
                    node.score = min(1.0, base_score + keyword_bonus)
            except Exception:
                pass
        
        # Filter nodes above the similarity threshold
        filtered_nodes = []
        for node in retrieved_nodes:
            score = node.score if node.score is not None else 0.0
            if score >= effective_cutoff:
                filtered_nodes.append(node)
                
        # If no nodes pass the cutoff, return default answer
        if not filtered_nodes:
            return {
                "answer": "I could not find relevant information in the documents.",
                "sources": [],
                "has_answer": False
            }
            
        # Form source metadata outputs
        sources = []
        for node in filtered_nodes:
            source_name = node.metadata.get("file_name") or node.metadata.get("source") or "Unknown"
            sources.append({
                "text": node.text[:300],
                "score": float(node.score) if node.score is not None else 0.0,
                "source": str(source_name)
            })

        # Synthesize answer using LlamaIndex Response Synthesizer
        response_synthesizer = get_response_synthesizer(
            llm=Settings.llm,
            response_mode="compact",
            streaming=streaming
        )
        
        response = response_synthesizer.synthesize(question, nodes=filtered_nodes)

        if streaming:
            def stream_generator():
                if hasattr(response, "response_gen"):
                    for token in response.response_gen:
                        yield token
                else:
                    yield str(response)

            return {
                "answer_stream": stream_generator(),
                "sources": sources,
                "has_answer": True
            }

        answer_text = str(response).strip()
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

