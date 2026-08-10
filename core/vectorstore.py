"""Qdrant client + hybrid (dense + sparse) search."""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVectorParams, SparseVector, Modifier,
    Prefetch, FusionQuery, Fusion,
)
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, TOP_K, EMBEDDING_DIM
from core.embeddings import embed_query, embed_texts, embed_query_sparse, embed_texts_sparse

_client = None

DENSE_NAME = "dense"
SPARSE_NAME = "sparse"


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
            vectors_config={
                DENSE_NAME: VectorParams(size=vector_size, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                SPARSE_NAME: SparseVectorParams(modifier=Modifier.IDF),
            },
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
    texts = [c["text"] for c in chunks]
    dense_vectors = embed_texts(texts)
    sparse_vectors = embed_texts_sparse(texts)

    points = [
        PointStruct(
            id=c["id"],
            vector={
                DENSE_NAME: dense_vec,
                SPARSE_NAME: SparseVector(indices=sparse_vec["indices"], values=sparse_vec["values"]),
            },
            payload={
                "text": c["text"],
                "category": c.get("category"),
                "title": c.get("title"),
                "source_file": c.get("source_file"),
            },
        )
        for c, dense_vec, sparse_vec in zip(chunks, dense_vectors, sparse_vectors)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    client = get_client()
    dense_vec = embed_query(query)
    sparse_vec = embed_query_sparse(query)

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        prefetch=[
            Prefetch(query=dense_vec, using=DENSE_NAME, limit=top_k * 4),
            Prefetch(
                query=SparseVector(indices=sparse_vec["indices"], values=sparse_vec["values"]),
                using=SPARSE_NAME,
                limit=top_k * 4,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
    ).points

    return [{"text": r.payload["text"], "score": r.score, "category": r.payload.get("category")} for r in results]










# """Qdrant client + search."""
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams, PointStruct
# from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, TOP_K, EMBEDDING_DIM
# from core.embeddings import embed_query, embed_texts

# _client = None


# def get_client() -> QdrantClient:
#     global _client
#     if _client is None:
#         _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
#     return _client


# def ensure_collection(vector_size: int = EMBEDDING_DIM):
#     client = get_client()
#     if not client.collection_exists(QDRANT_COLLECTION):
#         client.create_collection(
#             collection_name=QDRANT_COLLECTION,
#             vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
#         )

# def reset_collection():
#     """Delete and recreate the collection — use when chunking logic changes."""
#     client = get_client()
#     if client.collection_exists(QDRANT_COLLECTION):
#         client.delete_collection(QDRANT_COLLECTION)
#     ensure_collection()

# def upsert_chunks(chunks: list[dict]):
#     """chunks: [{id, text, category, title, source_id, source_file}, ...]"""
#     client = get_client()
#     vectors = embed_texts([c["text"] for c in chunks])
#     points = [
#         PointStruct(
#             id=c["id"],
#             vector=vec,
#             payload={
#                 "text": c["text"],
#                 "category": c.get("category"),
#                 "title": c.get("title"),
#                 "source_file": c.get("source_file"),
#             },
#         )
#         for c, vec in zip(chunks, vectors)
#     ]
#     client.upsert(collection_name=QDRANT_COLLECTION, points=points)


# def search(query: str, top_k: int = TOP_K) -> list[dict]:
#     client = get_client()
#     query_vector = embed_query(query)
#     results = client.query_points(
#         collection_name=QDRANT_COLLECTION,
#         query=query_vector,
#         limit=top_k,
#     ).points
#     return [{"text": r.payload["text"], "score": r.score, "category": r.payload.get("category")} for r in results]