from retriever import retrieve, MIN_SIMILARITY
from grounded import extract_quotes

K = 4

while True:
    question = input("\nAsk a question (or type q to quit): ")
    if question.strip().lower() == "q":
        break

    results, best_sim = retrieve(question, k=K)
    if best_sim < MIN_SIMILARITY:
        print("I couldn't find anything about that in your notes.")
        continue

    quotes = extract_quotes(question, results)
    if not quotes:
        print("I can't find that in the notes.")
        continue

    print("\nFrom your notes:\n")
    for q in quotes:
        where = f"page {q['page']}" if q["page"] != -1 else "document or code file"
        print(f'  "{q["quote"]}"')
        print(f"      ({q['source']}, {where})\n")