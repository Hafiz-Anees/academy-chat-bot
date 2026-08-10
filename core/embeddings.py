
"""Open-source embedding model wrappers using fastembed (ONNX, no torch needed)."""
from fastembed import TextEmbedding, SparseTextEmbedding
from config import EMBEDDING_MODEL, SPARSE_MODEL

_model = None
_sparse_model = None


def get_embedder() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def get_sparse_embedder() -> SparseTextEmbedding:
    global _sparse_model
    if _sparse_model is None:
        _sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL)
    return _sparse_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Dense embed a batch of texts, returns list of vectors."""
    embedder = get_embedder()
    return [vec.tolist() for vec in embedder.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def embed_texts_sparse(texts: list[str]) -> list[dict]:
    """Sparse embed a batch of texts, returns list of {indices, values} dicts."""
    embedder = get_sparse_embedder()
    return [{"indices": vec.indices.tolist(), "values": vec.values.tolist()} for vec in embedder.embed(texts)]


def embed_query_sparse(text: str) -> dict:
    return embed_texts_sparse([text])[0]















# """Open-source embedding model wrapper using fastembed (ONNX, no torch needed)."""
# from fastembed import TextEmbedding
# from config import EMBEDDING_MODEL

# _model = None


# def get_embedder() -> TextEmbedding:
#     global _model
#     if _model is None:
#         _model = TextEmbedding(model_name=EMBEDDING_MODEL)
#     return _model


# def embed_texts(texts: list[str]) -> list[list[float]]:
#     """Embed a batch of texts, returns list of vectors."""
#     embedder = get_embedder()
#     return [vec.tolist() for vec in embedder.embed(texts)]


# def embed_query(text: str) -> list[float]:
#     return embed_texts([text])[0]