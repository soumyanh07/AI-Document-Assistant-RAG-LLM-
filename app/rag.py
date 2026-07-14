from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentStore:
    def __init__(self) -> None:
        self.chunks: List[Dict[str, str]] = []
        self._vocabulary: List[str] = []
        self._document_vectors: List[List[float]] = []

    def add_document(self, path: Path, original_name: str) -> Dict[str, object]:
        text = extract_text(path)
        if not text.strip():
            raise ValueError(f"No readable text found in {path.name}")

        chunk_texts = chunk_text(text)
        for chunk in chunk_texts:
            self.chunks.append({"text": chunk, "source": original_name})

        self._rebuild_index()
        return {
            "name": original_name,
            "chunks": len(chunk_texts),
            "total_chunks": len(self.chunks),
        }

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, object]]:
        if not self.chunks:
            return []

        query_vector = build_tfidf_vector(query, self._vocabulary)
        scores = []
        for index, document_vector in enumerate(self._document_vectors):
            scores.append(
                cosine_similarity(query_vector, document_vector)
            )

        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        results: List[Dict[str, object]] = []
        for index, score in ranked[:top_k]:
            if score <= 0:
                continue
            results.append(
                {
                    "text": self.chunks[index]["text"],
                    "source": self.chunks[index]["source"],
                    "score": round(float(score), 3),
                }
            )
        return results

    def build_answer(self, question: str) -> str:
        results = self.search(question, top_k=4)
        if not results:
            return "No relevant content is available yet. Upload a document and try again."

        context = "\n".join([result["text"] for result in results])
        answer_lines = [
            f"Based on the uploaded documents, the most relevant information is:",
            "",
        ]
        for result in results[:3]:
            excerpt = str(result["text"]).strip()
            if len(excerpt) > 260:
                excerpt = excerpt[:257] + "..."
            answer_lines.append(f"- {excerpt}")

        answer_lines.append("")
        answer_lines.append(
            "If you want, I can also help turn this into a summary, flashcards, or a quiz."
        )
        return "\n".join(answer_lines)

    def _rebuild_index(self) -> None:
        if not self.chunks:
            self._vocabulary = []
            self._document_vectors = []
            return

        documents = [chunk["text"] for chunk in self.chunks]
        self._vocabulary, self._document_vectors = build_document_vectors(documents)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    if suffix == ".md":
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        document = DocxDocument(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text)
    if suffix == ".csv":
        return path.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported file type: {path.suffix}")


def chunk_text(text: str, max_chars: int = 700, overlap: int = 80) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks: List[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + max_chars, len(cleaned))
        if end < len(cleaned):
            split_point = cleaned.rfind(".", start, end)
            if split_point == -1:
                split_point = cleaned.rfind(" ", start, end)
            if split_point > start + max_chars // 2:
                end = split_point + 1
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start = max(start + max_chars - overlap, end - overlap)
    return chunks


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def build_document_vectors(documents: List[str]) -> tuple[List[str], List[List[float]]]:
    if not documents:
        return [], []

    tokenized_documents = [Counter(tokenize(document)) for document in documents]
    vocabulary = sorted({term for token_counts in tokenized_documents for term in token_counts})
    document_count = len(documents)

    idf_values = {
        term: math.log((1 + document_count) / (1 + sum(1 for token_counts in tokenized_documents if term in token_counts))) + 1.0
        for term in vocabulary
    }

    vectors: List[List[float]] = []
    for token_counts in tokenized_documents:
        vector = [token_counts.get(term, 0) * idf_values[term] for term in vocabulary]
        vectors.append(vector)

    return vocabulary, vectors


def build_tfidf_vector(text: str, vocabulary: List[str]) -> List[float]:
    token_counts = Counter(tokenize(text))
    if not vocabulary:
        return []

    return [token_counts.get(term, 0) for term in vocabulary]


def cosine_similarity(query_vector: List[float], document_vector: List[float]) -> float:
    if not query_vector or not document_vector:
        return 0.0

    dot_product = sum(q * d for q, d in zip(query_vector, document_vector))
    query_norm = math.sqrt(sum(q * q for q in query_vector))
    document_norm = math.sqrt(sum(d * d for d in document_vector))
    if query_norm == 0 or document_norm == 0:
        return 0.0
    return dot_product / (query_norm * document_norm)
