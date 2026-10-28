from retriever import retrieve, MIN_SIMILARITY
from grounded import extract_quotes

K = 4

should_answer = [
    "What is a leaf node?",
    "Explain merge sort step by step.",
    "What is a priority queue and which operations does it support?",
]
should_refuse = [
    "Compare Dijkstra's algorithm and Bellman-Ford. What are their limitations, and when should each be used?",
    "Explain how a hash table handles collisions. Compare separate chaining with open addressing.",
    "Compare dynamic programming, greedy algorithms, and backtracking. Explain when each approach is appropriate.",
    "Why does quick sort have an average time complexity of O(n log n) but a worst-case time complexity of O(n^2)?",
    "How does breadth first search visit the vertices of a graph level by level?",
]


def run(question):
    results, best_sim = retrieve(question, k=K)
    if best_sim < MIN_SIMILARITY:
        return []
    return extract_quotes(question, results)


answered_ok = 0
refused_ok = 0

for title, questions in (("SHOULD ANSWER", should_answer), ("SHOULD REFUSE", should_refuse)):
    print("\n" + "#" * 70 + "\n" + title)
    for q in questions:
        quotes = run(q)
        print("\nQ:", q)
        if not quotes:
            print("-> NO VERIFIED QUOTES (app says: I can't find that in the notes)")
            if title == "SHOULD REFUSE":
                refused_ok += 1
        else:
            print(f"-> {len(quotes)} verified quote(s)")
            for item in quotes:
                print(f'   "{item["quote"][:150]}" ({item["source"]}, page {item["page"]})')
            if title == "SHOULD ANSWER":
                answered_ok += 1

print("\n" + "=" * 70)
print(f"Answerable questions with a verified quote: {answered_ok} / {len(should_answer)}")
print(f"Refuse questions with no verified quote: {refused_ok} / {len(should_refuse)}")