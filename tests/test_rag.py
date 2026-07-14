from pathlib import Path

from backend.app.rag.document_store import DocumentStore


def test_document_store_indexes_text(tmp_path: Path) -> None:
    document_path = tmp_path / "notes.txt"
    document_path.write_text(
        "Python is a programming language used widely for AI and automation.",
        encoding="utf-8",
    )

    store = DocumentStore()
    result = store.add_document(document_path, document_path.name)

    assert result["chunks"] == 1
    assert len(store.chunks) == 1
    assert store.search("What language is used for AI?")[0]["source"] == document_path.name


def test_build_answer_returns_a_concise_summary(tmp_path: Path) -> None:
    document_path = tmp_path / "resume.txt"
    document_path.write_text(
        "John Doe is a senior software engineer with experience in Python, FastAPI, and cloud systems.",
        encoding="utf-8",
    )

    store = DocumentStore()
    store.add_document(document_path, document_path.name)

    answer = store.build_answer("What is John Doe's role?")

    assert "software engineer" in answer.lower()
    assert "Based on the uploaded documents" not in answer.lower()
    assert len(answer) < 250

