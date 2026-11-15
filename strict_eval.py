import sys
from eval_set import EVAL, OUT_OF_SCOPE
import retriever as R
from llm import answer_stream
from grounded import extract_quotes

REFUSAL = "can't find that in the notes"
GATE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.70   # python strict_eval.py 0.65
items = [e for e in EVAL if e["source"]]

def judge(q):
    results, best = R.retrieve(q, k=4)
    if best < GATE:
        return {"gate": True, "model": True, "quotes": True}   # already refused, skip the slow calls
    answer = "".join(answer_stream(q, results))
    model = REFUSAL in answer.lower().replace("\u2019", "'")
    quotes = len(extract_quotes(q, results)) == 0              # True = no verified quote found
    return {"gate": False, "model": model, "quotes": quotes}

def summarize(label, rows):
    n = len(rows)
    g = sum(r["gate"] for r in rows)
    m = sum(r["gate"] or r["model"] for r in rows)
    s = sum(r["gate"] or r["quotes"] for r in rows)
    b = sum(r["gate"] or r["model"] or r["quotes"] for r in rows)
    print(f"{label:<22} gate {g}/{n} | +model {m}/{n} | +quote check {s}/{n} | +both {b}/{n}")

print(f"gate = {GATE}")
out_rows = [judge(q) for q in OUT_OF_SCOPE]
in_rows = []
for e in items:
    r = judge(e["q"])
    in_rows.append(r)
    if r["quotes"] and not r["gate"]:
        print("  quote check found nothing for in-scope:", e["q"][:70])
print()
summarize("out-of-scope refused", out_rows)   # higher is better
summarize("in-scope refused", in_rows)        # lower is better