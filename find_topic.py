import sys
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
data = client.get_collection("dsa").get()

word = " ".join(sys.argv[1:]).lower()

for doc, meta in zip(data["documents"], data["metadatas"]):
    if word in doc.lower():
        print(meta["source"], "| page", meta["page"])