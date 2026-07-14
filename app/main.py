from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.rag import DocumentStore

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Document Assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
storage = DocumentStore()


class ChatRequest(BaseModel):
    question: str


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ok", "documents": len(storage.chunks)}


@app.post("/api/documents/upload")
async def upload_documents(files: List[UploadFile] = File(default=None)) -> dict[str, object]:
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded")

    saved_files: List[Path] = []
    results: List[dict[str, object]] = []
    for uploaded in files:
        if not uploaded.filename:
            continue
        destination = UPLOAD_DIR / uploaded.filename
        content = await uploaded.read()
        destination.write_bytes(content)
        saved_files.append(destination)

    for saved_path in saved_files:
        try:
            results.append(storage.add_document(saved_path, saved_path.name))
        except ValueError as exc:
            results.append({"name": saved_path.name, "error": str(exc)})

    return {"documents": results, "total_chunks": len(storage.chunks)}


@app.post("/api/chat")
async def chat(request: Request) -> dict[str, object]:
    if not storage.chunks:
        raise HTTPException(status_code=400, detail="Upload a document before asking a question")

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        form_data = await request.form()
        question = form_data.get("question")

    if not isinstance(question, str) or not question.strip():
        raise HTTPException(status_code=400, detail="Provide a non-empty question in the request body")

    answer = storage.build_answer(question)
    sources = storage.search(question, top_k=3)
    return {"answer": answer, "sources": sources}
