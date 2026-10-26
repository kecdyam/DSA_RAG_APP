from retriever import model, collection, bm25, tokenize, docs, metas, PREFIX

# Write 5 questions in YOUR words, avoiding the exact words your notes use.
# Include at least one with an exact technical term, like "heapify".
questions = [
    "which element is the very first one in a hierarchy of connected items",
    "how do I visit every vertex level by level",
    "heapify",
    # add 2 or more of your own
]

for q in questions:
    print("\n" + "=" * 60)
    print("Q:", q)

    q_vec = model.encode(PREFIX + q, normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=[q_vec], n_results=3)
    print("MEANING search:")
    for meta in res["metadatas"][0]:
        print("   ", meta["source"], "| page", meta["page"])

    scores = bm25.get_scores(tokenize(q))
    top = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:3]
    print("KEYWORD search:")
    for i in top:
        if scores[i] > 0:
            print("   ", metas[i]["source"], "| page", metas[i]["page"])