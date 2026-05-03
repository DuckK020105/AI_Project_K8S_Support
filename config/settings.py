"""
config/settings.py
Đọc .env một lần duy nhất qua pydantic-settings.
Tất cả giá trị giữ nguyên từ notebook gốc.
"""
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    gemini_api_key: str = ""

    # Dataset — giữ nguyên từ notebook
    dataset_name: str = "mcipriano/stackoverflow-kubernetes-questions"
    max_samples: int = 5000
    min_q_len: int = 30
    min_a_len: int = 100

    # Embedding
    embed_model: str = "intfloat/e5-base-v2"

    # Retrieval
    top_k_dense: int = 10
    top_k_sparse: int = 10
    top_k_final: int = 3
    dense_weight: float = 0.5
    sparse_weight: float = 0.5
    context_chars: int = 3000

    # LLM — giữ nguyên từ notebook
    gemini_model: str = "gemini-2.5-flash-lite"
    temperature: float = 0.1
    max_output_tokens: int = 1024

    # Storage — lưu vào folder data/
    faiss_dir: str = "data/faiss_k8s_lc"
    docs_cache_path: str = "data/docs_k8s.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
