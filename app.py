"""app.py — Streamlit entrypoint."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from src.ui import render_sidebar, render_history, render_input, CSS
from src.rag import load_data, build_or_load_indexes, build_chain, run_query

st.set_page_config(page_title="K8s Tech Support", page_icon="⎈", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in {"engine_status":"not_loaded","engine_error":"","history":[],"retriever":None,"chain":None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

from config import get_settings as _gs
if st.session_state.engine_status == "not_loaded" and _gs().gemini_api_key:
    st.session_state.engine_status = "loading"

# ── Sidebar ────────────────────────────────────────────────────────────────────
params = render_sidebar()

if params["clear_clicked"]:
    st.session_state.history = []
    st.rerun()

if params["load_clicked"]:
    if not params["api_key"]:
        st.error("Please enter a Gemini API key (or set GEMINI_API_KEY in .env).")
    else:
        st.session_state.engine_status = "loading"
        st.rerun()

if st.session_state.engine_status == "loading":
    with st.spinner("// Building index — first run takes ~3 min…"):
        try:
            docs      = load_data()
            retriever = build_or_load_indexes(docs, dense_weight=params["dense_w"], sparse_weight=params["sparse_w"])
            chain     = build_chain(retriever, top_k_final=params["top_k"], context_chars=params["ctx_chars"],
                                    gemini_model=params["model"], temperature=params["temperature"], api_key=params["api_key"])
            st.session_state.retriever     = retriever
            st.session_state.chain         = chain
            st.session_state.engine_status = "ready"
        except Exception as e:
            st.session_state.engine_status = "error"
            st.session_state.engine_error  = str(e)
    st.rerun()

# ── Top bar ────────────────────────────────────────────────────────────────────
status = st.session_state.engine_status
status_label = {"ready": "● READY", "loading": "● LOADING", "error": "● ERROR", "not_loaded": "● IDLE"}.get(status, "● IDLE")
status_color = {"ready": "#00ff9d", "loading": "#ffcc00", "error": "#ff4444", "not_loaded": "#1a5a7a"}.get(status, "#1a5a7a")

st.markdown(
    f'<div class="topbar">'
    f'  <span class="topbar-logo">⎈ K8s Tech Support</span>'
    f'  <span class="topbar-status" style="color:{status_color};font-family:\'JetBrains Mono\',monospace;font-size:0.68rem;letter-spacing:0.1em;margin-left:16px;">{status_label}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Welcome or chat ────────────────────────────────────────────────────────────
history = st.session_state.get("history", [])

if not history:
    ready = status == "ready"
    st.markdown(
        f'<div class="welcome-wrap">'
        f'  <div class="welcome-title">⎈ K8s Tech Support</div>'
        f'  <div class="welcome-sub">// Your Kubernetes production assistant</div>'
        f'  <div class="welcome-hint">{"Ask anything about Kubernetes below" if ready else "Open the sidebar → Load Index to get started"}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    render_history()

# ── Input ──────────────────────────────────────────────────────────────────────
if status != "ready":
    st.info("👈 Open the sidebar and click **Load Index** to get started.")
    st.stop()

st.session_state.chain = build_chain(
    st.session_state.retriever,
    top_k_final=params["top_k"], context_chars=params["ctx_chars"],
    gemini_model=params["model"], temperature=params["temperature"], api_key=params["api_key"],
)

query = render_input()
if query:
    st.session_state.history.append({"role": "user", "content": query})
    with st.spinner("// Retrieving & generating…"):
        result = run_query(st.session_state.chain, query)
    st.session_state.history.append({
        "role": "assistant", "content": result["answer"],
        "docs": result["doc_previews"], "latency": result["latency_s"],
    })
    st.rerun()
