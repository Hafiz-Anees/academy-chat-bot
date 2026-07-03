"""Qdrant client + search."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, TOP_K, EMBEDDING_DIM
from core.embeddings import embed_query, embed_texts

_client = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client


def ensure_collection(vector_size: int = EMBEDDING_DIM):
    client = get_client()
    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def reset_collection():
    """Delete and recreate the collection — use when chunking logic changes."""
    client = get_client()
    if client.collection_exists(QDRANT_COLLECTION):
        client.delete_collection(QDRANT_COLLECTION)
    ensure_collection()

def upsert_chunks(chunks: list[dict]):
    """chunks: [{id, text, category, title, source_id, source_file}, ...]"""
    client = get_client()
    vectors = embed_texts([c["text"] for c in chunks])
    points = [
        PointStruct(
            id=c["id"],
            vector=vec,
            payload={
                "text": c["text"],
                "category": c.get("category"),
                "title": c.get("title"),
                "source_file": c.get("source_file"),
            },
        )
        for c, vec in zip(chunks, vectors)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    client = get_client()
    query_vector = embed_query(query)
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
    ).points
    return [{"text": r.payload["text"], "score": r.score, "category": r.payload.get("category")} for r in results]