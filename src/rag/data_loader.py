"""
src/rag/data_loader.py
Load + clean dataset — giữ nguyên toàn bộ logic từ notebook:
strip_html, is_low_quality, dedup bằng md5 hash.
Cache kết quả vào docs_k8s.json để lần sau load nhanh.
"""
from __future__ import annotations

import re, json, hashlib
from pathlib import Path

from bs4 import BeautifulSoup
from datasets import load_dataset
from langchain_core.documents import Document
from tqdm.auto import tqdm

from config import get_settings


def strip_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "lxml")
    for code_tag in soup.find_all("code"):
        code_tag.replace_with(f" `{code_tag.get_text()}` ")
    for pre in soup.find_all("pre"):
        pre.replace_with(f"\n```\n{pre.get_text().strip()}\n```\n")
    text = soup.get_text(separator=" ")
    text = (text.replace("&amp;", "&").replace("&lt;", "<")
                .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"\s+", " ", text).strip()


def is_low_quality(answer: str) -> bool:
    a = answer.strip().lower()
    if len(a) < 100:
        return True
    if a.count("http") > 3 and len(a) < 200:
        return True
    patterns = [
        r"^(try|see|check|look at|refer to|please see)",
        r"^(yes|no|maybe|it depends)\.",
        r"^(this is a duplicate)",
    ]
    return any(re.match(p, a) for p in patterns)


def load_data(progress_callback=None) -> list[Document]:
    """
    Load dataset → clean → trả về list[Document].
    Cache vào disk để lần 2 trở đi load tức thì.
    progress_callback(current, total): optional, để update progress bar ngoài UI.
    """
    cfg = get_settings()
    cache_path = Path(cfg.docs_cache_path)

    # Load từ cache nếu có
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            raw = json.load(f)
        return [Document(page_content=d["content"], metadata=d["meta"]) for d in raw]

    # Pull từ HuggingFace + clean
    raw = load_dataset(cfg.dataset_name, split="train")
    limit = min(cfg.max_samples, len(raw))

    lc_docs, cache = [], []
    seen = set()
    skipped = {"short": 0, "low_quality": 0, "duplicate": 0}

    items = list(raw.select(range(limit)))
    for i, row in enumerate(tqdm(items, desc="Cleaning dataset")):
        q = strip_html(row.get("Question", ""))
        a = strip_html(row.get("Answer", ""))

        if len(q) < cfg.min_q_len or len(a) < cfg.min_a_len:
            skipped["short"] += 1
            continue
        if is_low_quality(a):
            skipped["low_quality"] += 1
            continue

        q_hash = hashlib.md5(re.sub(r"\s+", " ", q.lower()).encode()).hexdigest()
        if q_hash in seen:
            skipped["duplicate"] += 1
            continue
        seen.add(q_hash)

        content = f"Q: {q}\nA: {a}"
        meta = {"id": str(i), "question": q[:200]}
        lc_docs.append(Document(page_content=content, metadata=meta))
        cache.append({"content": content, "meta": meta})

        if progress_callback:
            progress_callback(i + 1, limit)

    # Lưu cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f)

    return lc_docs
