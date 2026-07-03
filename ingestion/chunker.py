"""Load markdown files (with YAML frontmatter), separate metadata from content,
and split the body into retrieval-sized chunks."""
import hashlib
from pathlib import Path
import frontmatter
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).parent.parent / "data" / "academy_docs"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n\n", "\n", " "],
)


def stable_id(text: str) -> int:
    """Deterministic id so re-running ingestion updates rather than duplicates."""
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)


def load_and_chunk() -> list[dict]:
    """
    Reads every .md file in data/academy_docs/.
    Frontmatter (id, title, category, course, etc.) becomes metadata,
    NOT part of the embedded/searchable text.
    Filename category is the fallback if frontmatter has no 'category'.
    """
    chunks = []
    for file in DATA_DIR.glob("*.md"):
        post = frontmatter.load(file)
        meta = post.metadata  # dict from YAML frontmatter
        body = post.content.strip()  # actual markdown, frontmatter stripped

        category = meta.get("category", file.stem)
        title = meta.get("title", file.stem)
        source_id = meta.get("id", file.stem)

        pieces = splitter.split_text(body)
        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if not piece:
                continue
            # Prepend title for context, since chunks are split away from the H1
            enriched_text = f"{title}\n{piece}" if title not in piece else piece

            chunks.append({
                "id": stable_id(f"{file.name}-{i}-{piece}"),
                "text": enriched_text,
                "category": category,
                "title": title,
                "source_id": source_id,
                "source_file": file.name,
            })
    return chunks