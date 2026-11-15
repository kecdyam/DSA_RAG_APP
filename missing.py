from pathlib import Path
import chromadb
c = chromadb.PersistentClient(path="chroma_db").list_collections()[0]
metas = c.get(include=["metadatas"])["metadatas"]
indexed = {}
for m in metas:
    indexed[m.get("source")] = indexed.get(m.get("source"), 0) + 1
on_disk = {f.name for f in Path("DATA").rglob("*") if f.is_file()}

print("--- on disk, NOT in index ---")
for n in sorted(on_disk - set(indexed)):
    print("  ", n)
print("--- in index, NOT on disk (stale) ---")
for n in sorted(set(indexed) - on_disk):
    print("  ", n, f"({indexed[n]} chunks)")
print("\nMerge_Sort chunks in index:", {k: v for k, v in indexed.items() if "merge" in k.lower()})