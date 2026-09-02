# pyrefly: ignore [missing-import]
import streamlit as st
import streamlit.components.v1 as components
import os
import shutil
from pathlib import Path


# Set up page configurations with SEO title
st.set_page_config(
    page_title="DocMind – AI Document & Website QA Engine with Citations",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dynamic Theme CSS Applier
def apply_theme_css(is_light: bool):
    if is_light:
        bg_color = "#f8fafc"
        text_color = "#0f172a"
        subtext_color = "#475569"
        sidebar_bg = "#f1f5f9"
        sidebar_border = "#cbd5e1"
        card_bg = "#ffffff"
        card_border = "#cbd5e1"
        tagline_color = "#475569"
        header_gradient = "linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)"
        code_bg = "#e2e8f0"
        code_color = "#0284c7"
        code_border = "#cbd5e1"
        input_bg = "#ffffff"
        input_border = "#cbd5e1"
        bottom_bar_bg = "#f8fafc"
        file_uploader_bg = "#ffffff"
        caret_color = "#0f172a"
        toggle_off_bg = "#64748b"
    else:
        bg_color = "#0d0e12"
        text_color = "#e2e8f0"
        subtext_color = "#94a3b8"
        sidebar_bg = "#161922"
        sidebar_border = "#2d3142"
        card_bg = "#1a1e29"
        card_border = "#334155"
        tagline_color = "#94a3b8"
        header_gradient = "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)"
        code_bg = "#1a1e29"
        code_color = "#38bdf8"
        code_border = "#334155"
        input_bg = "#161922"
        input_border = "#2d3142"
        bottom_bar_bg = "#0d0e12"
        file_uploader_bg = "#1a1e29"
        caret_color = "#38bdf8"
        toggle_off_bg = "#475569"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        * {{
            font-family: 'Outfit', sans-serif;
        }}
        
        /* Main App Background & Typography */
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        /* Bottom Chat Container Bar */
        section[data-testid="stBottom"],
        div[data-testid="stBottomBlockContainer"] {{
            background-color: {bottom_bar_bg} !important;
        }}

        /* Custom Sidebar design */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {{
            color: {text_color} !important;
        }}

        /* Inline Backtick Code Tags */
        code {{
            background-color: {code_bg} !important;
            color: {code_color} !important;
            border: 1px solid {code_border} !important;
            border-radius: 4px !important;
            padding: 2px 6px !important;
        }}

        /* File Uploader Dropzone */
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploaderDropzone"] {{
            background-color: {file_uploader_bg} !important;
            border: 2px dashed {card_border} !important;
            color: {text_color} !important;
        }}

        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] small {{
            color: {text_color} !important;
        }}

        div[data-testid="stFileUploader"] button {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border: 1px solid {card_border} !important;
        }}

        /* Form Inputs & Textarea (Scoped strictly to input elements, NOT toggle labels) */
        input[type="text"], input[type="number"], textarea, div[data-baseweb="input"] > input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border-color: {input_border} !important;
            caret-color: {caret_color} !important;
        }}

        /* Streamlit st.toggle Widget Styling (Targets data-testid="stToggle" switch button ONLY) */
        div[data-testid="stToggle"] [role="switch"],
        div[data-testid="stToggle"] label > div:first-of-type {{
            background-color: {toggle_off_bg} !important;
            border: 1px solid {toggle_off_bg} !important;
        }}

        div[data-testid="stToggle"] input:checked + div,
        div[data-testid="stToggle"] [role="switch"][aria-checked="true"] {{
            background-color: #ff4b4b !important;
            border: 1px solid #ff4b4b !important;
        }}

        div[data-testid="stToggle"] [role="switch"] > div,
        div[data-testid="stToggle"] label > div:first-of-type > div {{
            background-color: #ffffff !important;
        }}

        /* Ensure stToggle text labels have transparent background and clean text color */
        div[data-testid="stToggle"] p,
        div[data-testid="stToggle"] span,
        div[data-testid="stToggle"] label {{
            background-color: transparent !important;
            border: none !important;
            color: {text_color} !important;
        }}








        /* Tabs Styling */
        button[data-baseweb="tab"] {{
            color: {subtext_color} !important;
        }}
        
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #4f46e5 !important;
            border-bottom-color: #4f46e5 !important;
        }}

        /* Sliders */
        div[data-testid="stSlider"] p,
        div[data-testid="stSlider"] span,
        div[data-testid="stSlider"] div {{
            color: {text_color} !important;
        }}

        /* Expanders */
        div[data-testid="stExpander"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 8px !important;
        }}

        div[data-testid="stExpander"] summary span {{
            color: {text_color} !important;
        }}

        /* Glassmorphic title headers */
        .app-header {{
            background: {header_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 3rem;
            margin-bottom: 0.2rem;
        }}
        
        .app-tagline {{
            color: {tagline_color} !important;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }}
        
        /* Custom style for source expander */
        .source-block {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
        }}
        
        .source-header {{
            font-weight: 600;
            color: #0284c7 !important;
        }}
        
        .source-score {{
            font-size: 0.85rem;
            color: #10b981 !important;
        }}
        
        /* Styling button */
        .stButton>button {{
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }}
        .stButton>button:hover {{
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4) !important;
        }}
        
        /* Chat Messages */
        div[data-testid="stChatMessage"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }}
        
        div[data-testid="stChatMessage"] p,
        div[data-testid="stChatMessage"] span,
        div[data-testid="stChatMessage"] div {{
            color: {text_color} !important;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


# Apply theme CSS based on persistent session state
is_light_theme = st.session_state.get("is_light_mode", False)
apply_theme_css(is_light_theme)


# Try importing dependencies and handle environment configuration error elegantly
try:
    from ingest import ingest_source, get_indexed_documents, delete_document, clear_knowledge_base
    from query import answer
    import config
    config_error = None
except ValueError as e:
    config_error = str(e)

def get_indexing_loader_html(title: str, subtitle: str, is_light: bool) -> str:
    """Returns HTML for an animated scanning loader card rendered in the main right content area during ingestion."""
    card_bg = "#ffffff" if is_light else "#161922"
    border_color = "#cbd5e1" if is_light else "#334155"
    title_color = "#0f172a" if is_light else "#f8fafc"
    subtitle_color = "#475569" if is_light else "#94a3b8"
    track_bg = "#e2e8f0" if is_light else "#272d3d"

    return f"""
    <style>
        @keyframes pulse-brain {{
            0% {{ transform: scale(1); filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4)); }}
            50% {{ transform: scale(1.15); filter: drop-shadow(0 0 22px rgba(124, 58, 237, 0.85)); }}
            100% {{ transform: scale(1); filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4)); }}
        }}
        @keyframes progress-slide {{
            0% {{ width: 5%; }}
            50% {{ width: 75%; }}
            100% {{ width: 98%; }}
        }}
        .loader-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 36px 24px;
            text-align: center;
            margin: 24px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        }}
        .loader-icon {{
            font-size: 3.8rem;
            animation: pulse-brain 1.5s infinite ease-in-out;
            display: inline-block;
            margin-bottom: 12px;
        }}
        .loader-title {{
            font-weight: 700;
            font-size: 1.35rem;
            color: {title_color};
            margin-bottom: 6px;
        }}
        .loader-subtitle {{
            color: {subtitle_color};
            font-size: 0.95rem;
            margin-bottom: 24px;
        }}
        .progress-track {{
            width: 100%;
            height: 8px;
            background-color: {track_bg};
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 50%, #38bdf8 100%);
            animation: progress-slide 2.5s infinite ease-in-out;
            border-radius: 10px;
        }}
    </style>
    <div class="loader-card">
        <div class="loader-icon">🧠</div>
        <div class="loader-title">{title}</div>
        <div class="loader-subtitle">{subtitle}</div>
        <div class="progress-track">
            <div class="progress-fill"></div>
        </div>
    </div>
    """


# Main area loader placeholder for displaying active indexing animation
main_loader_placeholder = st.empty()


# Sidebar UI
with st.sidebar:
    st.markdown("<h1 style='margin: 0; font-size: 4rem; line-height: 1;'>🧠</h1>", unsafe_allow_html=True)
    st.markdown("### DocMind Core")
    st.markdown("---")
    
    if config_error:
        st.error(config_error)
        st.stop()

    # Display single clean floating toast notification across reruns
    if "action_status" in st.session_state:
        _, status_msg, status_icon = st.session_state.pop("action_status")
        st.toast(status_msg, icon=status_icon)

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
                    
                    # Display animated scanner loader in main content area
                    main_loader_placeholder.markdown(
                        get_indexing_loader_html(
                            "Indexing Reference Documents...",
                            "Parsing files, generating text chunks, and embedding vectors into ChromaDB",
                            is_light_theme
                        ),
                        unsafe_allow_html=True
                    )
                    
                    num_chunks, num_docs = ingest_source(str(TEMP_DIR))
                    if num_chunks == 0:
                        st.session_state["action_status"] = ("info", "Document content is already indexed in the vector store.", "ℹ️")
                    else:
                        st.session_state["action_status"] = ("success", f"Successfully indexed {num_chunks} chunks from {num_docs} documents.", "✅")
                    st.rerun()
                except Exception as e:
                    st.session_state["action_status"] = ("error", f"Error during ingestion: {e}", "⚠️")
                    st.rerun()
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
                    # Display animated scanner loader in main content area
                    main_loader_placeholder.markdown(
                        get_indexing_loader_html(
                            "Scraping & Indexing Website...",
                            "Fetching web page content, parsing HTML, and extracting vector embeddings",
                            is_light_theme
                        ),
                        unsafe_allow_html=True
                    )
                    
                    num_chunks, num_docs = ingest_source(web_url)
                    if num_chunks == 0:
                        st.session_state["action_status"] = ("info", "Website content is already indexed.", "ℹ️")
                    else:
                        st.session_state["action_status"] = ("success", f"Successfully indexed {num_chunks} chunks from 1 web page.", "✅")
                    st.rerun()
                except Exception as e:
                    st.session_state["action_status"] = ("error", f"Error during website ingestion: {e}", "⚠️")
                    st.rerun()


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
                        if deleted_count > 0:
                            st.session_state["action_status"] = ("success", f"Successfully deleted '{doc['file_name']}' ({deleted_count} chunks removed).", "🗑️")
                        else:
                            st.session_state["action_status"] = ("error", f"Could not find or delete chunks for '{doc['file_name']}'.", "⚠️")
                        st.rerun()

            st.markdown("---")
            confirm_clear = st.checkbox("Confirm clear knowledge base", key="confirm_clear_cb")
            if st.button("🔴 Clear All Data", key="clear_all_btn"):
                if confirm_clear:
                    success = clear_knowledge_base()
                    if success:
                        st.session_state["action_status"] = ("success", "Knowledge base has been completely reset.", "🧹")
                    else:
                        st.session_state["action_status"] = ("error", "Failed to reset knowledge base.", "⚠️")
                    st.rerun()
                else:
                    st.warning("Please check the confirmation box first.")

                    
    st.markdown("---")
    st.markdown("### ⚙️ Control Panel")
    
    # Theme Toggle & Dynamic parameter sliders
    is_light_theme = st.toggle("☀️ Light Theme", value=st.session_state.get("is_light_mode", False), key="light_theme_toggle")
    if is_light_theme != st.session_state.get("is_light_mode", False):
        st.session_state["is_light_mode"] = is_light_theme
        apply_theme_css(is_light_theme)
        st.rerun()


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

# Main area loader placeholder for displaying active indexing animation
main_loader_placeholder = st.empty()


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

def render_copy_button(text: str, key_suffix: str = "", is_light: bool = False):
    """Renders an icon-only Copy to Clipboard button (standard SVG double-rectangle icon) adapted for current theme."""
    import json
    safe_text = json.dumps(text)
    btn_id = f"btn_{abs(hash(text))}_{key_suffix}"
    svg_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
    check_icon = '<span style="color: #10b981; font-weight: bold; font-size: 13px;">✓</span>'

    btn_bg = "#ffffff" if is_light else "#1a1e29"
    btn_border = "#cbd5e1" if is_light else "#334155"
    btn_color = "#475569" if is_light else "#94a3b8"
    hover_bg = "#f1f5f9" if is_light else "#272d3d"

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
          background-color: {btn_bg};
          border: 1px solid {btn_border};
          color: {btn_color};
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
          background-color: {hover_bg};
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
            btn.style.borderColor = "{btn_border}";
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
            render_copy_button(message["content"], f"hist_{idx}", is_light=is_light_theme)
            
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
        render_copy_button(prompt, "user_live", is_light=is_light_theme)
    
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
            render_copy_button(answer_text, "asst_live", is_light=is_light_theme)


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
