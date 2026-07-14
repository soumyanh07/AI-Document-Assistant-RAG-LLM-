from pathlib import Path

from app.rag import DocumentStore


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
