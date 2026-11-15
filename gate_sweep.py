from eval_set import EVAL, OUT_OF_SCOPE
import retriever as R

items = [e for e in EVAL if e["source"]]
out = [R.retrieve(q, k=1)[1] for q in OUT_OF_SCOPE]
inn = [R.retrieve(e["q"], k=1)[1] for e in items]
print("threshold   out-of-scope refused   in-scope wrongly refused")
for t in [0.60, 0.65, 0.68, 0.70, 0.72, 0.74, 0.76, 0.80]:
    print(f"{t:>9.2f}   {sum(s < t for s in out):>10}/{len(out)}   {sum(s < t for s in inn):>16}/{len(inn)}")