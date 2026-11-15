import sys, chromadb
c = chromadb.PersistentClient(path="chroma_db").list_collections()[0]
data = c.get(include=["documents", "metadatas"])
kw = " ".join(sys.argv[1:]).lower()
hits = {}
for doc, meta in zip(data["documents"], data["metadatas"]):
    if kw in doc.lower():
        hits[meta.get("source", "?")] = hits.get(meta.get("source", "?"), 0) + 1
print(hits or "NOT FOUND in any chunk")