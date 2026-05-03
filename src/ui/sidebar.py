"""src/ui/sidebar.py"""
from __future__ import annotations
import streamlit as st
from config import get_settings
from .styles import STATUS_HTML


def render_sidebar() -> dict:
    cfg = get_settings()

    with st.sidebar:
        st.markdown("## ⎈ K8s Tech Support")
        st.caption("// Kubernetes Q&A Assistant")
        st.divider()

        default_key = cfg.gemini_api_key or st.session_state.get("api_key", "")
        api_key = st.text_input(
            "GEMINI_API_KEY",
            value=default_key,
            type="password",
            placeholder="AIza… (or set in .env)",
        )
        if api_key:
            st.session_state["api_key"] = api_key
        if cfg.gemini_api_key:
            st.caption("✅ Loaded from .env")

        st.divider()
        st.caption("// MODEL")
        model = st.selectbox("Gemini model", ["gemini-2.5-flash-lite", "gemini-2.5-flash"], index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, cfg.temperature, step=0.05)

        st.divider()
        st.caption("// RETRIEVAL")
        top_k     = st.slider("Top-k docs", 1, 6, cfg.top_k_final)
        ctx_chars = st.slider("Context chars / doc", 500, 5000, cfg.context_chars, step=100)
        dense_w   = st.slider("Dense weight (FAISS)", 0.0, 1.0, cfg.dense_weight, step=0.1)
        sparse_w  = round(1.0 - dense_w, 1)
        st.caption(f"Sparse weight (BM25): {sparse_w}")

        st.divider()
        status = st.session_state.get("engine_status", "not_loaded")
        st.markdown(STATUS_HTML.get(status, STATUS_HTML["not_loaded"]), unsafe_allow_html=True)
        if status == "error":
            st.caption(st.session_state.get("engine_error", ""))

        load_clicked = st.button(
            "🔄 Reload Index" if status == "ready" else "🚀 Load Index",
            use_container_width=True,
            disabled=(status == "loading"),
        )
        st.divider()
        clear_clicked = st.button("🗑️ Clear Chat", use_container_width=True)
        st.caption("Dataset: stackoverflow-kubernetes  \nEmbed: intfloat/e5-base-v2  \nFusion: RRF (c=60)")

    return {
        "api_key": api_key, "top_k": top_k, "ctx_chars": ctx_chars,
        "dense_w": dense_w, "sparse_w": sparse_w, "model": model,
        "temperature": temperature, "load_clicked": load_clicked, "clear_clicked": clear_clicked,
    }
