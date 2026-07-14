# AI Document Assistant (RAG + LLM)

## Project structure

```text
AI-Document-Assistant/

backend/
    app/
        api/
        auth/
        chat/
        embeddings/
        parser/
        rag/
        database/
        models/
        services/
        utils/

frontend/
    src/
        components/
        pages/
        hooks/
        context/
        api/

docker/

tterraform/

.github/workflows/

tests/
```

## Run locally

1. Install dependencies: `pip install -r requirements_mine.txt`
2. Start the app: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`

