"""Shared configuration for Lab 18."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM configuration ---
# OpenRouter exposes an OpenAI-compatible API. OPENAI_API_KEY is retained as a
# fallback so existing .env files continue to work.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_API_KEY = OPENROUTER_API_KEY or OPENAI_API_KEY
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
LLM_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") if OPENROUTER_API_KEY else os.getenv("OPENAI_BASE_URL", "")

# RAGAS/LangChain read the conventional OpenAI environment variables. Point
# them at OpenRouter as well when an OpenRouter key is configured.
if OPENROUTER_API_KEY:
    # Assign rather than setdefault: a stale/empty OPENAI_API_KEY from the
    # shell must not prevent RAGAS/LangChain from receiving the Router key.
    os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
    os.environ["OPENAI_BASE_URL"] = LLM_BASE_URL
    os.environ["OPENAI_API_BASE"] = LLM_BASE_URL
    os.environ["OPENAI_MODEL_NAME"] = LLM_MODEL


def get_llm_client():
    """Return an OpenAI-compatible client configured for OpenRouter or OpenAI."""
    from openai import OpenAI

    kwargs = {"api_key": LLM_API_KEY, "timeout": 20}
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    if OPENROUTER_API_KEY:
        kwargs["default_headers"] = {
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "Lab 18 Production RAG"),
        }
    return OpenAI(**kwargs)

# --- Qdrant ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "lab18_production"
NAIVE_COLLECTION = "lab18_naive"

# --- Embedding ---
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# --- Chunking ---
HIERARCHICAL_PARENT_SIZE = 2048
HIERARCHICAL_CHILD_SIZE = 256
SEMANTIC_THRESHOLD = 0.85

# --- Search ---
BM25_TOP_K = 20
DENSE_TOP_K = 20
HYBRID_TOP_K = 20
RERANK_TOP_K = 3

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_SET_PATH = os.path.join(os.path.dirname(__file__), "test_set.json")
