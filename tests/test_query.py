import os
import pytest
from unittest.mock import MagicMock, patch

# Enable testing mode in config
os.environ["TESTING"] = "true"

import config
from query import answer

class MockNode:
    """Mock node implementation imitating LlamaIndex NodeWithScore."""
    def __init__(self, text, score, metadata):
        self.text = text
        self.score = score
        self.metadata = metadata

@patch("query.OpenAIEmbedding")
@patch("query.GeminiEmbedding")
@patch("query.Anthropic")
@patch("query.Gemini")
@patch("query.chromadb.PersistentClient")
@patch("query.VectorStoreIndex")
@patch("query.get_response_synthesizer")
def test_answer_success(
    mock_synth_cls, mock_index_cls, mock_chroma_cls, mock_gemini_cls, mock_anthropic_cls, mock_gemini_embed_cls, mock_openai_embed_cls
):

    """Test standard query success: returns LLM answer, parses citations, filters out low scores."""
    # Mock Chroma Client and Collection
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 1
    
    mock_collection_obj = MagicMock()
    mock_collection_obj.name = "docmind"
    mock_client.list_collections.return_value = [mock_collection_obj]
    mock_client.get_collection.return_value = mock_collection
    mock_chroma_cls.return_value = mock_client

    # Mock Retriever and Nodes
    mock_index = MagicMock()
    mock_retriever = MagicMock()
    
    node1 = MockNode("RAG stands for Retrieval-Augmented Generation.", 0.85, {"file_name": "sample.txt"})
    node2 = MockNode("Embeddings convert words into vectors.", 0.75, {"file_name": "sample.txt"})
    node3 = MockNode("Other topic information.", 0.40, {"file_name": "sample.txt"})  # below 0.7 cutoff
    
    mock_retriever.retrieve.return_value = [node1, node2, node3]
    mock_index.as_retriever.return_value = mock_retriever
    mock_index_cls.from_vector_store.return_value = mock_index

    # Mock Response Synthesizer
    mock_synthesizer = MagicMock()
    mock_response = MagicMock()
    mock_response.__str__.return_value = "Retrieval-Augmented Generation (RAG) is a technique..."
    mock_synthesizer.synthesize.return_value = mock_response
    mock_synth_cls.return_value = mock_synthesizer

    res = answer("What is RAG?")

    assert res["has_answer"] is True
    assert res["answer"] == "Retrieval-Augmented Generation (RAG) is a technique..."
    assert len(res["sources"]) == 2  # Node 3 filtered out
    assert res["sources"][0]["score"] == 0.85
    assert res["sources"][0]["source"] == "sample.txt"
    assert res["sources"][1]["score"] == 0.75

@patch("query.OpenAIEmbedding")
@patch("query.GeminiEmbedding")
@patch("query.Anthropic")
@patch("query.Gemini")
@patch("query.chromadb.PersistentClient")
@patch("query.VectorStoreIndex")
@patch("query.get_response_synthesizer")
def test_answer_no_relevant_info(
    mock_synth_cls, mock_index_cls, mock_chroma_cls, mock_gemini_cls, mock_anthropic_cls, mock_gemini_embed_cls, mock_openai_embed_cls
):

    """Test query fallback when all retrieved nodes fall below similarity threshold."""
    # Mock Chroma Client and Collection
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 1
    
    mock_collection_obj = MagicMock()
    mock_collection_obj.name = "docmind"
    mock_client.list_collections.return_value = [mock_collection_obj]
    mock_client.get_collection.return_value = mock_collection
    mock_chroma_cls.return_value = mock_client

    # Mock Retriever returning low score nodes
    mock_index = MagicMock()
    mock_retriever = MagicMock()
    
    node1 = MockNode("Completely unrelated content.", 0.45, {"file_name": "sample.txt"})
    
    mock_retriever.retrieve.return_value = [node1]
    mock_index.as_retriever.return_value = mock_retriever
    mock_index_cls.from_vector_store.return_value = mock_index

    res = answer("What is RAG?")

    assert res["has_answer"] is False
    assert res["answer"] == "I could not find relevant information in the documents."
    assert len(res["sources"]) == 0

@patch("query.OpenAIEmbedding")
@patch("query.GeminiEmbedding")
@patch("query.Anthropic")
@patch("query.Gemini")
@patch("query.chromadb.PersistentClient")
@patch("query.VectorStoreIndex")
@patch("query.get_response_synthesizer")
def test_answer_streaming_and_chat_history(
    mock_synth_cls, mock_index_cls, mock_chroma_cls, mock_gemini_cls, mock_anthropic_cls, mock_gemini_embed_cls, mock_openai_embed_cls
):
    """Test answer with streaming enabled and past chat history."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 1
    
    mock_collection_obj = MagicMock()
    mock_collection_obj.name = "docmind"
    mock_client.list_collections.return_value = [mock_collection_obj]
    mock_client.get_collection.return_value = mock_collection
    mock_chroma_cls.return_value = mock_client

    mock_index = MagicMock()
    mock_retriever = MagicMock()
    node1 = MockNode("RAG stands for Retrieval-Augmented Generation.", 0.85, {"file_name": "sample.txt"})
    mock_retriever.retrieve.return_value = [node1]
    mock_index.as_retriever.return_value = mock_retriever
    mock_index_cls.from_vector_store.return_value = mock_index

    mock_synthesizer = MagicMock()
    mock_response = MagicMock()
    mock_response.response_gen = iter(["Retrieval ", "Augmented ", "Generation"])
    mock_synthesizer.synthesize.return_value = mock_response
    mock_synth_cls.return_value = mock_synthesizer

    history = [
        {"role": "user", "content": "Tell me about RAG"},
        {"role": "assistant", "content": "RAG enhances LLMs with external data."}
    ]

    res = answer(
        question="Summarize its benefits",
        chat_history=history,
        streaming=True,
        top_k=5,
        hybrid_search=True
    )

    assert res["has_answer"] is True
    assert "answer_stream" in res
    stream_output = "".join(list(res["answer_stream"]))
    assert stream_output == "Retrieval Augmented Generation"

