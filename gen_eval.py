from retriever import retrieve, MIN_SIMILARITY
from llm import answer_stream

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
        return "I couldn't find anything about that in your notes."
    return "".join(answer_stream(question, results))


def label(answer):
    a = answer.lower().replace("\u2019", "'")
    if "can't find that in the notes" in a or "couldn't find anything" in a:
        return "REFUSED"
    if "do not cover" in a or "does not cover" in a or "not covered" in a:
        return "GAP STATED"
    return "ANSWERED"


for title, questions in (("SHOULD ANSWER", should_answer), ("SHOULD REFUSE", should_refuse)):
    print("\n" + "#" * 70 + "\n" + title)
    for q in questions:
        answer = run(q)
        print("\nQ:", q)
        print("->", label(answer))
        print(answer)