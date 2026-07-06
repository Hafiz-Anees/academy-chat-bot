# # pip install qdrant-client
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env file
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Connect
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

print("✅ Connected to Qdrant successfully")


collections = client.get_collections()

for collection in collections.collections:
    print(collection.name)



points, _ = client.scroll(
    collection_name="academy-knowledge-base",
    limit=10,
    with_payload=True,
    with_vectors=False
)

for p in points:
    print("=" * 50)
    print(p.payload)
   











# info = client.get_collection("CDC-Callbot-2026")

# print(info)


# points, _ = client.scroll(
#     collection_name="CDC-Callbot-2026",
#     limit=10,   # change this to see more data
#     with_payload=True,
#     with_vectors=False
# )

# for p in points:
#     print(p)

# want to see payload only

# points, _ = client.scroll(
#     collection_name="CDC-Callbot-2026",
#     limit=10,
#     with_payload=True,
#     with_vectors=False
# )

# for p in points:
#     print(p.payload)

