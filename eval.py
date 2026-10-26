from retriever import retrieve, MIN_SIMILARITY

K = 5  # how many chunks we look at

# parts = None   -> not filled in yet (the script just shows what it found)
# parts = []     -> this topic is NOT in my notes, the app should refuse
# parts = [...]  -> one entry per topic the question needs
# Java and Word files use page -1.

tests = [
    # --- theory questions ---
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
    {"q": "How do I build a max-heap from an array?",
     "parts": [{"name": "build heap", "where": [("HEAP_SORT.pdf", 2)]}]},
    {"q": "How does quick sort divide an array and sort the pieces?",
     "parts": [{"name": "quick sort idea", "where": [("Quick_Sort.docx", -1)]}]},
    {"q": "Explain merge sort step by step.",
     "parts": [{"name": "merge sort", "where": [("Merge_Sort.docx", -1)]}]},

    # --- reworded questions (the words differ from the notes) ---
    {"q": "What do we call a node that has no children?",
     "parts": [{"name": "leaf node reworded", "where": [("Trre_Module3.pdf", 1)]}]},
    {"q": "How many edges does a tree with N nodes have?",
     "parts": [{"name": "edge count", "where": [("Trre_Module3.pdf", 3)]}]},

    # --- code questions (the word "java" switches code mode on) ---
    {"q": "Show the java code to insert a node at the front of a linked list",
     "parts": [{"name": "insert at front", "where": [
         ("LinkedListCreation.java", -1), ("LinkedListDeletion.java", -1),
         ("Singly_Linked_List_Searching.pdf", 1), ("Singly_Linked_List_Searching.pdf", 2)]}]},
    {"q": "Show the java code for a queue using an array",
     "parts": [{"name": "queue code", "where": [("QueueUsingArray.java", -1)]}]},
    {"q": "Show the java code for a sparse matrix",
     "parts": [{"name": "sparse matrix code", "where": [("SparseMatrix.java", -1)]}]},

    # --- "should refuse" tests: my notes do not answer these ---
    {"q": "Compare Dijkstra's algorithm and Bellman-Ford. What are their limitations, and when should each be used?", "parts": []},
    {"q": "Explain how a hash table handles collisions. Compare separate chaining with open addressing.", "parts": []},
    {"q": "Compare dynamic programming, greedy algorithms, and backtracking. Explain when each approach is appropriate.", "parts": []},
    # notes cover the topic but NOT this detail:
    {"q": "Why does quick sort have an average time complexity of O(n log n) but a worst-case time complexity of O(n^2)?", "parts": []},
    {"q": "How does breadth first search visit the vertices of a graph level by level?", "parts": []},
]

scored = 0
total_recall = 0.0
total_rr = 0.0
refusal_tests = 0
refusals_ok = 0

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
        refusal_tests += 1
        refused = best_sim < MIN_SIMILARITY
        refusals_ok += refused
        print("-> expected: NOT in notes |", "refused (good)" if refused else "did NOT refuse (bad)")
        continue

    parts_found = 0
    first_rank = None
    for part in parts:
        ranks = [found.index(loc) + 1 for loc in part["where"] if loc in found]
        ok = len(ranks) > 0
        parts_found += ok
        if ok:
            best = min(ranks)
            first_rank = best if first_rank is None else min(first_rank, best)
        print(f"   [{'x' if ok else ' '}] {part['name']}")

    recall = parts_found / len(parts)
    rr = 1 / first_rank if first_rank else 0
    total_recall += recall
    total_rr += rr
    scored += 1
    print(f"-> recall: {parts_found}/{len(parts)} | first correct result at rank: {first_rank}")

print("\n" + "=" * 70)
if scored:
    print(f"Average recall over {scored} scored questions: {round(total_recall / scored, 2)}")
    print(f"MRR over {scored} scored questions: {round(total_rr / scored, 2)}")
if refusal_tests:
    print(f"Refused correctly: {refusals_ok} / {refusal_tests}")