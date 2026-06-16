import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Enable testing mode in config
os.environ["TESTING"] = "true"

from ingest import load_url, ingest_source

def test_load_url_success():
    """Test downloading and extracting text content from a web URL."""
    mock_response = MagicMock()
    mock_response.content = b"<html><head><title>Test Title</title></head><body><h1>Hello World</h1><p>This is a RAG test content.</p></body></html>"
    mock_response.raise_for_status = MagicMock()
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        docs = load_url("https://example.com/test-page")
        assert len(docs) == 1
        assert "Test Title" in docs[0].text
        assert "Hello World" in docs[0].text
        assert "This is a RAG test content." in docs[0].text
        assert docs[0].metadata["source"] == "https://example.com/test-page"
        assert docs[0].metadata["file_name"] == "Test Title"
        mock_get.assert_called_once()

def test_load_url_failure():
    """Test load_url behaves correctly and raises ValueError on request failures."""
    import requests
    with patch("requests.get", side_effect=requests.exceptions.RequestException("Connection Error")):
        with pytest.raises(ValueError) as excinfo:
            load_url("https://example.com/bad-page")
        assert "Failed to fetch content from URL" in str(excinfo.value)


@patch("ingest.OpenAIEmbedding")
@patch("ingest.GeminiEmbedding")
@patch("ingest.SentenceSplitter")
@patch("ingest.chromadb.PersistentClient")
@patch("ingest.VectorStoreIndex")
@patch("ingest.SimpleDirectoryReader")
def test_ingest_source_local_file(
    mock_reader_cls, mock_index_cls, mock_chroma_cls, mock_splitter_cls, mock_gemini_embed_cls, mock_openai_embed_cls
):

    """Test ingesting local files is properly parsed, chunked, and stored in vector DB."""
    # Mocking SimpleDirectoryReader
    mock_reader = MagicMock()
    mock_doc = MagicMock()
    mock_doc.text = "Sample text here"
    mock_reader.load_data.return_value = [mock_doc]
    mock_reader_cls.return_value = mock_reader

    # Mocking Node Parser / Splitter
    mock_splitter = MagicMock()
    mock_node = MagicMock()
    mock_node.text = "Sample text chunk"
    mock_node.score = 0.95
    mock_node.metadata = {"file_name": "sample.txt"}
    mock_splitter.get_nodes_from_documents.return_value = [mock_node]
    mock_splitter_cls.return_value = mock_splitter

    # Mocking Chroma DB
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_chroma_cls.return_value = mock_client

    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.is_file", return_value=True):
        
        num_chunks, num_docs = ingest_source("docs/sample.txt")
        
        assert num_chunks == 1
        assert num_docs == 1
        mock_reader_cls.assert_called_once_with(input_files=["docs/sample.txt"])
        mock_index_cls.assert_called_once()

def test_ingest_source_not_found():
    """Test ingest_source raises FileNotFoundError for missing local files."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            ingest_source("nonexistent_file.txt")
