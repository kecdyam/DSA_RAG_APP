from retriever import retrieve, MIN_SIMILARITY

K = 5  # how many chunks we look at

# parts = None   -> not filled in yet (the script just shows what it found)
# parts = []     -> this topic is NOT in my notes, the app should refuse
# parts = [...]  -> one entry per topic the question needs
# Java files use page -1.

tests = [
    # --- theory questions (retrieval tests) ---
    {"q": "What are root nodes, leaf nodes and internal nodes in a tree?",
     "parts": [
         {"name": "root and leaf", "where": [("Trre_Module3.pdf", 1)]},
         {"name": "internal node", "where": [("Trre_Module3.pdf", 2)]},
     ]},
    {"q": "What is a priority queue and which operations does it support?",
     "parts": [{"name": "priority queue", "where": [("HEAP_SORT.pdf", 4)]}]},
    {"q": "What are breadth first search and depth first search?",
     "parts": [
         {"name": "BFS", "where": [("Graph_Module6_Lecture5.pdf", 5)]},
         {"name": "DFS", "where": [("Graph_Module6_Lecture5.pdf", 5), ("Graph_Module6_Lecture5.pdf", 7)]},
     ]},

    # --- code questions (the word "java" switches code mode on) ---
    {"q": "Show the java code to insert a node at the front of a linked list",
     "parts": [{"name": "insert at front", "where": [
         ("LinkedListCreation.java", -1), ("LinkedListDeletion.java", -1),
         ("Singly_Linked_List_Searching.pdf", 1), ("Singly_Linked_List_Searching.pdf", 2)]}]},
    {"q": "Show the java code for a queue using an array",
     "parts": [{"name": "queue code", "where": [("QueueUsingArray.java", -1)]}]},
    {"q": "Show the java code for a sparse matrix",
     "parts": [{"name": "sparse matrix code", "where": [("SparseMatrix.java", -1)]}]},

    # --- honesty tests: not in my notes, the app should refuse ---
    {"q": "Why does quicksort have an average time complexity of O(n log n) but a worst-case time complexity of O(n^2)?", "parts": []},
    {"q": "Compare Dijkstra's algorithm and Bellman-Ford. What are their limitations, and when should each be used?", "parts": []},
    {"q": "Explain how a hash table handles collisions. Compare separate chaining with open addressing.", "parts": []},
    {"q": "Compare dynamic programming, greedy algorithms, and backtracking. Explain when each approach is appropriate.", "parts": []},
]

scored = 0
total_recall = 0.0

for number, t in enumerate(tests, start=1):
    results, best_sim = retrieve(t["q"], k=K)
    found = [(r["source"], r["page"]) for r in results]

    print("\n" + "=" * 70)
    print(f"Q{number}: {t['q']}")
    print("Top results:")
    for rank, (source, page) in enumerate(found, start=1):
        print(f"  {rank}. {source} | page {page}")
    print(f"Best similarity: {round(best_sim, 3)}")

    parts = t["parts"]

    if parts is None:
        print("-> TODO: open these pages, then fill in 'parts' for this question")
        continue

    if parts == []:
        refused = best_sim < MIN_SIMILARITY
        print("-> expected: NOT in notes |", "refused (good)" if refused else "did NOT refuse (bad)")
        continue

    parts_found = 0
    for part in parts:
        ok = any(loc in found for loc in part["where"])
        parts_found += ok
        print(f"   [{'x' if ok else ' '}] {part['name']}")
    recall = parts_found / len(parts)
    total_recall += recall
    scored += 1
    print(f"-> recall: {parts_found}/{len(parts)}")

if scored:
    print(f"\nAverage recall over {scored} scored questions: {round(total_recall / scored, 2)}")