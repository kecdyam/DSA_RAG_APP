import sys
import chromadb

if len(sys.argv) < 2:
    print("Usage: python show_chunks.py FILE_NAME [PAGE]")
    print('Example: python show_chunks.py "Trre_Module3.pdf" 1')
    sys.exit()

data = chromadb.PersistentClient(path="chroma_db").get_collection("dsa").get()
name = sys.argv[1]
page = sys.argv[2] if len(sys.argv) > 2 else None

for doc, meta in zip(data["documents"], data["metadatas"]):
    if meta["source"] == name and (page is None or str(meta["page"]) == page):
        print("-----", meta["source"], "| page", meta["page"])
        print(doc)