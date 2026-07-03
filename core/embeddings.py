"""Open-source embedding model wrapper using fastembed (ONNX, no torch needed)."""
from fastembed import TextEmbedding
from config import EMBEDDING_MODEL

_model = None


def get_embedder() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts, returns list of vectors."""
    embedder = get_embedder()
    return [vec.tolist() for vec in embedder.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]