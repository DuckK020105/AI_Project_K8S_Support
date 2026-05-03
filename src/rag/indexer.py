"""
src/rag/indexer.py
Build FAISS (dense) + BM25 (sparse) → EnsembleRetriever (RRF fusion).
Giữ nguyên logic từ notebook: FAISS lưu/load disk, BM25 build mỗi lần.
"""
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_classic.retrievers import EnsembleRetriever

from config import get_settings


def build_or_load_indexes(
    lc_docs: list[Document],
    dense_weight: float | None = None,
    sparse_weight: float | None = None,
) -> EnsembleRetriever:
    """
    Trả về hybrid_retriever (EnsembleRetriever).
    FAISS: load từ disk nếu đã có, ngược lại build + save.
    BM25: build mới mỗi lần (nhanh, không cần cache).
    """
    cfg = get_settings()
    dw = dense_weight  if dense_weight  is not None else cfg.dense_weight
    sw = sparse_weight if sparse_weight is not None else cfg.sparse_weight

    # ── Embedding model ────────────────────────────────────────────────────────
    embed_model = HuggingFaceEmbeddings(
        model_name=cfg.embed_model,
        encode_kwargs={"normalize_embeddings": True, "batch_size": 256},
        model_kwargs={"device": "cpu"},
    )

    # ── FAISS (Dense) ──────────────────────────────────────────────────────────
    faiss_dir = cfg.faiss_dir
    if Path(faiss_dir).exists():
        faiss_store = FAISS.load_local(
            faiss_dir, embed_model, allow_dangerous_deserialization=True
        )
    else:
        faiss_store = FAISS.from_documents(lc_docs, embed_model)
        faiss_store.save_local(faiss_dir)

    # ── BM25 (Sparse) ──────────────────────────────────────────────────────────
    bm25 = BM25Retriever.from_documents(lc_docs)
    bm25.k = cfg.top_k_sparse

    # ── EnsembleRetriever — RRF fusion ─────────────────────────────────────────
    faiss_ret = faiss_store.as_retriever(search_kwargs={"k": cfg.top_k_dense})
    hybrid = EnsembleRetriever(
        retrievers=[faiss_ret, bm25],
        weights=[dw, sw],
        c=60,  # RRF constant theo paper gốc
    )

    return hybrid
