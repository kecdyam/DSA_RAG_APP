import sys, chromadb
kw = " ".join(sys.argv[1:]).lower()
c = chromadb.PersistentClient(path="chroma_db").list_collections()[0]
d = c.get(include=["documents", "metadatas"])
for doc, m in zip(d["documents"], d["metadatas"]):
    i = doc.lower().find(kw)
    if i != -1:
        print(m.get("source"), "| page", m.get("page"), "|", repr(doc[max(0, i - 100):i + 200]))