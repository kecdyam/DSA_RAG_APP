import chromadb

client = chromadb.PersistentClient(path="chroma_db")
data = client.get_collection("dsa").get()

topics = [
    "merge sort", "quick sort", "quicksort", "heap sort", "binary search",
    "dijkstra", "bellman", "hash", "collision", "chaining", "open addressing",
    "dynamic programming", "greedy", "backtracking",
    "stack", "queue", "linked list", "bfs", "dfs", "time complexity",
]

for topic in topics:
    places = []
    for doc, meta in zip(data["documents"], data["metadatas"]):
        if topic in doc.lower():
            places.append((meta["source"], meta["page"]))
    print(f"{topic:22} {len(places):3} chunks", places[:3])