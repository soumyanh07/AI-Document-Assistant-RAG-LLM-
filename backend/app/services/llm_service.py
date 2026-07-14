from __future__ import annotations

from typing import List


def is_openai_available() -> bool:
    return False


def embed_texts(texts: List[str]) -> List[List[float]]:
    return [[] for _ in texts]


def embed_query(query: str) -> List[float]:
    return []


def generate_answer(question: str, sources: List[str]) -> str:
    return ""
