# pyrefly: ignore [missing-import]
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
    
    /* Hide Streamlit brandings and developer menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Try importing dependencies and handle environment configuration error elegantly
try:
    from ingest import ingest_source, get_indexed_documents, delete_document, clear_knowledge_base
    from query import answer
    import config
    config_error = None
except ValueError as e:
    config_error = str(e)

# Sidebar UI
with st.sidebar:
    st.markdown("<h1 style='margin: 0; font-size: 4rem; line-height: 1;'>🧠</h1>", unsafe_allow_html=True)
    st.markdown("### DocMind Core")
    st.markdown("---")
    
    if config_error:
        st.error(config_error)
        st.stop()

    st.subheader("📚 Knowledge Base")
    tab1, tab2, tab3 = st.tabs(["📁 Upload", "🌐 Website", "🗂️ Manage"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Upload reference documents",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            key="file_uploader"
        )
        index_btn = st.button("Index documents", key="index_files_btn")
        
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
                        if num_chunks == 0:
                            st.toast("Document content is already indexed in the vector store.", icon="ℹ️")
                        else:
                            st.toast(f"Successfully indexed {num_chunks} chunks from {num_docs} documents.", icon="✅")
                except Exception as e:
                    st.error(f"Error during ingestion: {e}")
                finally:
                    if TEMP_DIR.exists():
                        shutil.rmtree(TEMP_DIR)
                        
    with tab2:
        web_url = st.text_input(
            "Enter website URL",
            placeholder="https://example.com/article",
            key="web_url_input"
        )
        index_url_btn = st.button("Index website", key="index_url_btn")
        
        if index_url_btn:
            if not web_url:
                st.warning("Please enter a website URL first.")
            elif not web_url.startswith(("http://", "https://")):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                try:
                    with st.spinner("Scraping and indexing website..."):
                        num_chunks, num_docs = ingest_source(web_url)
                        if num_chunks == 0:
                            st.toast("Website content is already indexed.", icon="ℹ️")
                        else:
                            st.toast(f"Successfully indexed {num_chunks} chunks from 1 web page.", icon="✅")
                except Exception as e:
                    st.error(f"Error during website ingestion: {e}")


    with tab3:
        indexed_docs = get_indexed_documents()
        if not indexed_docs:
            st.caption("No documents currently indexed.")
        else:
            st.markdown(f"**Total Documents**: `{len(indexed_docs)}`")
            for doc in indexed_docs:
                with st.expander(f"📄 {doc['file_name']}", expanded=False):
                    st.write(f"**Source**: `{doc['source']}`")
                    st.write(f"**Chunks**: `{doc['chunk_count']}`")
                    st.write(f"**Indexed At**: `{doc['indexed_at']}`")
                    if st.button(f"🗑️ Delete Document", key=f"del_{doc['source']}"):
                        deleted_count = delete_document(doc['source'])
                        st.toast(f"Deleted {deleted_count} chunks from '{doc['file_name']}'.", icon="🗑️")
                        st.rerun()

            st.markdown("---")
            confirm_clear = st.checkbox("Confirm clear knowledge base", key="confirm_clear_cb")
            if st.button("🔴 Clear All Data", key="clear_all_btn"):
                if confirm_clear:
                    clear_knowledge_base()
                    st.toast("Knowledge base reset successfully.", icon="🧹")
                    st.rerun()
                else:
                    st.warning("Please check the confirmation box first.")

                    
    st.markdown("---")
    st.markdown("### ⚙️ Control Panel")
    
    # Dynamic parameter sliders and controls
    default_top_k = int(getattr(config, "TOP_K", 5))
    default_cutoff = float(getattr(config, "SIMILARITY_CUTOFF", 0.35))
    top_k = st.slider("Top K Candidates", min_value=1, max_value=10, value=default_top_k, key="top_k_slider")
    similarity_cutoff = st.slider("Min Similarity Score", min_value=0.0, max_value=1.0, value=default_cutoff, step=0.05, key="cutoff_slider")
    hybrid_search = st.toggle("Enable BM25 Hybrid Search", value=getattr(config, "HYBRID_SEARCH", True), key="hybrid_toggle")
    enable_streaming = st.toggle("Token Streaming Response", value=True, key="stream_toggle")


    embed_provider = "OpenAI" if config.OPENAI_API_KEY else "Google Gemini"
    llm_provider = "Anthropic (Claude)" if config.ANTHROPIC_API_KEY else "Google Gemini"
    active_backend = f"{embed_provider} (Embeddings) + {llm_provider} (LLM)"

    st.caption(f"**Active Backend**: `{active_backend}`")
    st.caption(f"**Collection**: `{config.COLLECTION_NAME}`")




# Main Area UI
st.markdown('<div class="app-header">DocMind</div>', unsafe_allow_html=True)
st.markdown('<div class="app-tagline">Ask anything about your documents or website URLs — get answers with citations.</div>', unsafe_allow_html=True)

# Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat history button in main UI toolbar
if st.session_state.messages:
    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        if st.button("🧹 Clear Chat", key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()

import streamlit.components.v1 as components

def render_copy_button(text: str, key_suffix: str = ""):
    """Renders an icon-only Copy to Clipboard button (standard SVG double-rectangle icon) for chat messages."""
    import json
    safe_text = json.dumps(text)
    btn_id = f"btn_{abs(hash(text))}_{key_suffix}"
    svg_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
    check_icon = '<span style="color: #10b981; font-weight: bold; font-size: 13px;">✓</span>'

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{
          margin: 0;
          padding: 0;
          background: transparent;
          display: flex;
          justify-content: flex-end;
          align-items: center;
        }}
        .copy-btn {{
          background-color: #1a1e29;
          border: 1px solid #334155;
          color: #94a3b8;
          border-radius: 6px;
          width: 28px;
          height: 28px;
          padding: 0;
          cursor: pointer;
          transition: all 0.2s ease;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }}
        .copy-btn:hover {{
          background-color: #272d3d;
          color: #f1f5f9;
          border-color: #475569;
        }}
      </style>
    </head>
    <body>
      <button id="{btn_id}" class="copy-btn" title="Copy to clipboard" onclick="copyText()">{svg_icon}</button>
      <script>
        function copyText() {{
          const val = {safe_text};
          navigator.clipboard.writeText(val);
          const btn = document.getElementById("{btn_id}");
          btn.innerHTML = '{check_icon}';
          btn.style.borderColor = "#10b981";
          setTimeout(function() {{
            btn.innerHTML = '{svg_icon}';
            btn.style.borderColor = "#334155";
          }}, 2000);
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=32)


# Display conversation history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("content"):
            render_copy_button(message["content"], f"hist_{idx}")
            
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("🔍 Citations & Sources"):
                for s_idx, src in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-block">
                        <span class="source-header">[{s_idx + 1}] Source: {src['source']}</span> | 
                        <span class="source-score">Match Score: {src['score']:.4f}</span>
                        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 6px; font-style: italic;">
                            "...{src['text']}..."
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        if message["role"] == "assistant" and not message.get("has_answer", True):
            st.warning("No relevant information found in the documents.")

# Message input
if prompt := st.chat_input("Ask a question about your documents or website URLs..."):
    # Render user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
        render_copy_button(prompt, "user_live")
    
    # Generate response
    with st.chat_message("assistant"):
        res = answer(
            question=prompt,
            chat_history=st.session_state.messages,
            top_k=top_k,
            similarity_cutoff=similarity_cutoff,
            hybrid_search=hybrid_search,
            streaming=enable_streaming
        )
        
        if enable_streaming and res.get("answer_stream"):
            answer_text = st.write_stream(res["answer_stream"])
        else:
            answer_text = res.get("answer", "")
            st.markdown(answer_text)
            
        if answer_text:
            render_copy_button(answer_text, "asst_live")

        if res["has_answer"] and res["sources"]:
            with st.expander("🔍 Citations & Sources"):
                for s_idx, src in enumerate(res["sources"]):
                    st.markdown(f"""
                    <div class="source-block">
                        <span class="source-header">[{s_idx + 1}] Source: {src['source']}</span> | 
                        <span class="source-score">Match Score: {src['score']:.4f}</span>
                        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 6px; font-style: italic;">
                            "...{src['text']}..."
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        elif not res["has_answer"]:
            st.warning("No relevant information found in the documents.")

            
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "sources": res.get("sources", []),
            "has_answer": res.get("has_answer", True)
        })
