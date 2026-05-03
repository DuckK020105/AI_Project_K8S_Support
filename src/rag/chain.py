"""
src/rag/chain.py
LCEL chain: HybridRetriever → format_context → Prompt → Gemini → StrOutput.
Giữ nguyên structure từ notebook.
"""
from __future__ import annotations

import time

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from config import get_settings
from .prompt import build_prompt


def format_context(docs: list[Document], ctx_chars: int) -> str:
    """
    Format list[Document] → context string cho LLM.
    Giữ nguyên logic từ notebook.
    """
    if not docs:
        return "NO_RELEVANT_DOCS"
    parts = []
    for i, doc in enumerate(docs, 1):
        content = doc.page_content
        if len(content) > ctx_chars:
            content = content[:ctx_chars] + "..."
        parts.append(f"[Doc {i}]\n{content}")
    return "\n\n---\n\n".join(parts)


def build_chain(
    hybrid_retriever,
    top_k_final: int | None = None,
    context_chars: int | None = None,
    gemini_model: str | None = None,
    temperature: float | None = None,
    api_key: str | None = None,
):
    """
    Build LCEL chain. Gọi lại khi user thay đổi params — index không rebuild.
    """
    cfg = get_settings()

    _top_k    = top_k_final   if top_k_final   is not None else cfg.top_k_final
    _ctx      = context_chars if context_chars  is not None else cfg.context_chars
    _model    = gemini_model  if gemini_model   is not None else cfg.gemini_model
    _temp     = temperature   if temperature    is not None else cfg.temperature
    _key      = api_key       if api_key        else cfg.gemini_api_key

    llm = ChatGoogleGenerativeAI(
        model=_model,
        google_api_key=_key,
        temperature=_temp,
        max_output_tokens=cfg.max_output_tokens,
    )

    prompt = build_prompt()

    chain = (
        RunnablePassthrough.assign(
            retrieved_docs=RunnableLambda(
                lambda x: hybrid_retriever.invoke(x["question"])[:_top_k]
            )
        )
        | RunnablePassthrough.assign(
            context=RunnableLambda(
                lambda x: format_context(x["retrieved_docs"], _ctx)
            )
        )
        | {
            "answer":   prompt | llm | StrOutputParser(),
            "docs":     lambda x: x["retrieved_docs"],
            "question": lambda x: x["question"],
        }
    )
    return chain


def run_query(chain, question: str) -> dict:
    """Chạy chain, trả về dict chuẩn để UI dùng."""
    t0 = time.time()
    result = chain.invoke({"question": question})
    latency = round(time.time() - t0, 1)

    doc_previews = [
        d.metadata.get("question", d.page_content[:80])
        for d in result["docs"]
    ]
    return {
        "answer":       result["answer"],
        "doc_previews": doc_previews,
        "latency_s":    latency,
        "n_sources":    len(result["docs"]),
    }
