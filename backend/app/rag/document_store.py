import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from docx import Document as DocxDocument
from pypdf import PdfReader

from backend.app.services.llm_service import (
    embed_query,
    embed_texts,
    generate_answer,
    is_openai_available,
)

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "what",
    "when",
    "where",
    "from",
    "into",
    "about",
    "your",
    "their",
    "have",
    "has",
    "been",
    "were",
    "will",
    "can",
    "could",
    "should",
    "does",
    "did",
    "is",
    "are",
    "was",
    "were",
    "a",
    "an",
    "of",
    "to",
    "in",
    "on",
    "at",
    "be",
    "or",
    "as",
    "if",
    "it",
    "its",
    "my",
    "our",
    "you",
    "we",
    "they",
    "me",
    "us",
    "them",
    "who",
    "whom",
    "which",
    "how",
    "why",
    "do",
    "does",
    "did",
}


class DocumentStore:
    def __init__(self) -> None:
        self.chunks: List[Dict[str, str]] = []
        self._vocabulary: List[str] = []
        self._idf: List[float] = []
        self._document_vectors: List[List[float]] = []
        self._document_embeddings: List[List[float]] = []

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

        results: List[tuple[float, int, Dict[str, str]]] = []
        if self._document_embeddings:
            try:
                query_embedding = embed_query(query)
                for index, chunk in enumerate(self.chunks):
                    score = cosine_similarity(query_embedding, self._document_embeddings[index])
                    if score > 0:
                        results.append((score, index, chunk))
            except Exception:
                self._document_embeddings = []

        if not results:
            query_vector = build_tfidf_vector(query, self._vocabulary, self._idf)
            if query_vector and any(query_vector):
                for index, chunk in enumerate(self.chunks):
                    score = cosine_similarity(query_vector, self._document_vectors[index])
                    if score > 0:
                        results.append((score, index, chunk))

        results.sort(key=lambda item: item[0], reverse=True)
        ranked: List[Dict[str, object]] = []
        for score, _, chunk in results[:top_k]:
            ranked.append(
                {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "score": round(float(score), 3),
                }
            )
        
        if not ranked and self.chunks:
            for chunk in self.chunks[:top_k]:
                ranked.append(
                    {
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "score": 0.0,
                    }
                )
        
        return ranked

    def build_answer(self, question: str) -> str:
        results = self.search(question, top_k=6)
        if not results:
            return "No relevant content is available yet. Upload a document and try again."

        answer = ""
        if is_openai_available():
            try:
                answer = generate_answer(question, [result["text"] for result in results])
            except Exception:
                answer = ""

        if not answer:
            answer = synthesize_answer(question, [result["text"] for result in results])
        if not answer:
            answer = str(results[0]["text"]).strip()
        if len(answer) > 500:
            answer = answer[:497] + "..."
        return answer

    def _rebuild_index(self) -> None:
        if not self.chunks:
            self._vocabulary = []
            self._idf = []
            self._document_vectors = []
            self._document_embeddings = []
            return

        documents = [chunk["text"] for chunk in self.chunks]
        self._vocabulary, self._idf, self._document_vectors = build_document_vectors(documents)
        if is_openai_available():
            try:
                self._document_embeddings = embed_texts(documents)
            except Exception:
                self._document_embeddings = []


def normalize_text(text: str) -> str:
    cleaned = text.replace("\x00", "")
    cleaned = cleaned.replace("ﬁ", "fi").replace("ﬂ", "fl")
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"(?<=\w)-\s+(?=\w)", "", cleaned)
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    return cleaned.strip()


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return normalize_text(path.read_text(encoding="utf-8"))
    if suffix == ".md":
        return normalize_text(path.read_text(encoding="utf-8"))
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [normalize_text(page.extract_text() or "") for page in reader.pages]
        return "\n".join(page for page in pages if page)
    if suffix == ".docx":
        document = DocxDocument(str(path))
        return normalize_text("\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text))
    if suffix == ".csv":
        return normalize_text(path.read_text(encoding="utf-8"))
    raise ValueError(f"Unsupported file type: {path.suffix}")


def chunk_text(text: str, max_chars: int = 700, overlap: int = 80) -> List[str]:
    cleaned = normalize_text(text)
    if len(cleaned) <= max_chars:
        return [cleaned]

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if len(sentences) == 1:
        return [cleaned]

    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = sentence
        else:
            chunks.append(sentence)

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        merged: List[str] = []
        for index, chunk in enumerate(chunks):
            if index == 0:
                merged.append(chunk)
                continue
            prev = merged[-1]
            if len(prev) + len(chunk) < max_chars:
                merged[-1] = f"{prev} {chunk}".strip()
            else:
                merged.append(chunk)
        chunks = merged
    return chunks


def tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"\b\w+\b", text.lower()) if len(token) > 2 and token not in STOPWORDS]


def extract_keywords(text: str) -> List[str]:
    return list(dict.fromkeys(tokenize(text)))


def score_chunk(query_terms: List[str], chunk_text: str) -> float:
    if not query_terms:
        return 0.0
    normalized_chunk = normalize_text(chunk_text).lower()
    if not normalized_chunk:
        return 0.0

    match_count = sum(1 for term in query_terms if term in normalized_chunk)
    if match_count == 0:
        return 0.0
    return match_count / len(query_terms)


def synthesize_answer(question: str, chunks: List[str]) -> str:
    query_terms = extract_keywords(question)
    if not chunks:
        return ""

    best_sentences: List[str] = []
    for chunk in chunks:
        sentence = get_best_sentence(query_terms, chunk)
        if sentence and sentence not in best_sentences:
            best_sentences.append(sentence)
        if len(best_sentences) >= 3:
            break

    if best_sentences:
        return " ".join(best_sentences)

    combined = " ".join(chunks[:2])
    return normalize_text(combined)[:500]


def get_best_sentence(query_terms: List[str], context: str) -> str:
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", normalize_text(context)) if segment.strip()]
    best_sentence = ""
    best_score = -1
    for sentence in sentences:
        score = sum(1 for term in query_terms if term in sentence.lower())
        if score > best_score:
            best_score = score
            best_sentence = sentence
    return best_sentence if best_score > 0 else ""


def build_document_vectors(documents: List[str]) -> Tuple[List[str], List[float], List[List[float]]]:
    tokenized_docs = [tokenize(document) for document in documents]
    vocabulary = sorted({token for tokens in tokenized_docs for token in tokens})
    if not vocabulary:
        return [], [], []

    document_frequencies = Counter()
    for tokens in tokenized_docs:
        document_frequencies.update(set(tokens))

    idf_values = [math.log((len(documents) + 1) / (document_frequencies[token] + 1)) + 1 for token in vocabulary]
    vectors: List[List[float]] = []
    for tokens in tokenized_docs:
        term_counts = Counter(tokens)
        vector = [term_counts[token] * idf for token, idf in zip(vocabulary, idf_values)]
        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 0:
            vector = [value / norm for value in vector]
        vectors.append(vector)

    return vocabulary, idf_values, vectors


def build_tfidf_vector(text: str, vocabulary: List[str], idf_values: List[float]) -> List[float]:
    if not vocabulary:
        return []

    term_counts = Counter(tokenize(text))
    vector = [term_counts[token] * idf for token, idf in zip(vocabulary, idf_values)]
    norm = math.sqrt(sum(value * value for value in vector))
    if norm > 0:
        vector = [value / norm for value in vector]
    return vector


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0

    return sum(a * b for a, b in zip(vector_a, vector_b))
