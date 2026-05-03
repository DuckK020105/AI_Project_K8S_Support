"""src/ui/chat.py"""
from __future__ import annotations
import streamlit as st


def render_history():
    for msg in st.session_state.get("history", []):
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            docs  = msg.get("docs", [])
            chips = "".join(f'<span class="doc-chip">[{i+1}] {d[:70]}…</span>' for i, d in enumerate(docs))
            meta  = f'<div class="meta-row">📚 {len(docs)} docs retrieved · ⏱ {msg.get("latency","?")}s</div>'
            st.markdown('<div class="chat-assistant">', unsafe_allow_html=True)
            st.markdown(msg["content"])
            st.markdown(f'<div class="doc-chips">{chips}{meta}</div></div>', unsafe_allow_html=True)


def render_input() -> str | None:
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([11, 1])
        user_input = cols[0].text_input("q", placeholder="Ask a Kubernetes question…", label_visibility="collapsed")
        submitted  = cols[1].form_submit_button("▶", use_container_width=True)
    if submitted and user_input.strip():
        return user_input.strip()
    return None
