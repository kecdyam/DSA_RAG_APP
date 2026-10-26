import chromadb
from sentence_transformers import SentenceTransformer
from chunker import all_chunks

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

client = chromadb.PersistentClient(path="chroma_db")

# start fresh each time so we never store duplicates
try:
    client.delete_collection("dsa")
except Exception:
    pass
collection = client.create_collection("dsa", metadata={"hnsw:space": "cosine"})

texts = [c["text"] for c in all_chunks]
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True).tolist()
ids = [f"chunk_{i}" for i in range(len(all_chunks))]
metadatas = [
    {
        "source": c["source"],
        "page": c["page"] if c["page"] is not None else -1,
        "type": c["type"],
    }
    for c in all_chunks
]

collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
print("Stored chunks:", collection.count())