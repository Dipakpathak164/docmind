import streamlit as st
import os
import shutil
from pathlib import Path

# Set up page configurations
st.set_page_config(
    page_title="DocMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful visual design (Premium Dark Mode feel)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply typography */
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container background */
    .stApp {
        background-color: #0d0e12;
        color: #e2e8f0;
    }
    
    /* Custom Sidebar design */
    section[data-testid="stSidebar"] {
        background-color: #161922;
        border-right: 1px solid #2d3142;
    }
    
    /* Glassmorphic title headers */
    .app-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.2rem;
    }
    
    .app-tagline {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Custom style for source expander */
    .source-block {
        background-color: #1a1e29;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
    }
    
    .source-header {
        font-weight: 600;
        color: #38bdf8;
    }
    
    .source-score {
        font-size: 0.85rem;
        color: #10b981;
    }
    
    /* Styling button */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Try importing dependencies and handle environment configuration error elegantly
try:
    from ingest import ingest_source
    from query import answer
    import config
    config_error = None
except ValueError as e:
    config_error = str(e)

# Sidebar UI
with st.sidebar:
    st.image("https://img.icons8.com/gradient/100/brain.png", width=80)
    st.markdown("### DocMind Core")
    st.markdown("---")
    
    if config_error:
        st.error(config_error)
        st.stop()
        
    st.subheader("📚 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload reference documents",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )
    
    index_btn = st.button("Index documents")
    
    if index_btn:
        if not uploaded_files:
            st.warning("Please upload at least one document first.")
        else:
            TEMP_DIR = Path("./temp_uploads")
            if TEMP_DIR.exists():
                shutil.rmtree(TEMP_DIR)
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            
            try:
                for uploaded_file in uploaded_files:
                    file_path = TEMP_DIR / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                with st.spinner("Processing & embedding chunks..."):
                    num_chunks, num_docs = ingest_source(str(TEMP_DIR))
                    st.success(f"Successfully indexed {num_chunks} chunks from {num_docs} documents.")
            except Exception as e:
                st.error(f"Error during ingestion: {e}")
            finally:
                if TEMP_DIR.exists():
                    shutil.rmtree(TEMP_DIR)
                    
    st.markdown("---")
    st.markdown("### Settings")
    st.info(
        f"**Collection**: `{config.COLLECTION_NAME}`\n"
        f"**Chunk Size**: `{config.CHUNK_SIZE}`\n"
        f"**Overlap**: `{config.CHUNK_OVERLAP}`\n"
        f"**Min Similarity**: `{config.SIMILARITY_CUTOFF}`"
    )

# Main Area UI
st.markdown('<div class="app-header">DocMind</div>', unsafe_allow_html=True)
st.markdown('<div class="app-tagline">Ask anything about your documents — get answers with citations.</div>', unsafe_allow_html=True)

# Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("🔍 Citations & Sources"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-block">
                        <span class="source-header">[{idx + 1}] Source: {src['source']}</span> | 
                        <span class="source-score">Match Score: {src['score']:.4f}</span>
                        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 6px; font-style: italic;">
                            "...{src['text']}..."
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        if message["role"] == "assistant" and not message.get("has_answer", True):
            st.warning("No relevant information found in the documents.")

# Message input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Render user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing documents and generating response..."):
            res = answer(prompt)
            st.markdown(res["answer"])
            
            if res["has_answer"] and res["sources"]:
                with st.expander("🔍 Citations & Sources"):
                    for idx, src in enumerate(res["sources"]):
                        st.markdown(f"""
                        <div class="source-block">
                            <span class="source-header">[{idx + 1}] Source: {src['source']}</span> | 
                            <span class="source-score">Match Score: {src['score']:.4f}</span>
                            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 6px; font-style: italic;">
                                "...{src['text']}..."
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            elif not res["has_answer"]:
                st.warning("No relevant information found in the documents.")
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": res["answer"],
                "sources": res.get("sources", []),
                "has_answer": res.get("has_answer", True)
            })
