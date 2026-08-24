from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.embeddings import get_embedder
from core.vectorstore import get_client, ensure_collection
from routers import health, chat, webhook

app = FastAPI(title="Academy Admissions Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(webhook.router)


@app.on_event("startup")
async def startup_event():
    print("Warming up embedding model...")
    get_embedder()

    print("Connecting to Qdrant...")
    get_client()
    ensure_collection()

    print("Startup warm-up complete.")