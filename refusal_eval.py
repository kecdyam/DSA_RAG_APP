from eval_set import OUT_OF_SCOPE
import retriever as R
from llm import answer_stream

REFUSAL = "can't find that in the notes"
gate = model = answered = 0
for q in OUT_OF_SCOPE:
    results, best = R.retrieve(q, k=4)
    if best < R.MIN_SIMILARITY:
        gate += 1
        print(f"GATE      {best:.2f}  {q[:60]}")
        continue
    ans = "".join(answer_stream(q, results))
    if REFUSAL in ans.lower().replace("\u2019", "'"):
        model += 1
        print(f"MODEL     {best:.2f}  {q[:60]}")
    else:
        answered += 1
        print(f"ANSWERED  {best:.2f}  {q[:50]} | {ans[:80]!r}")
n = len(OUT_OF_SCOPE)
print(f"\nrefused by gate {gate}, by model {model}, answered anyway {answered} of {n} "
      f"(correct refusal {(gate + model) / n:.0%})")