import ollama

MODEL = "llama3.2:3b"

SYSTEM = (
    "You answer questions using ONLY the notes provided. "
    "If the notes do not contain the answer, reply exactly: "
    "I can't find that in the notes. "
    "Do not use outside knowledge."
)

paragraph = (
    "A leaf node is a node that has no child nodes. "
    "The root is the topmost node of a tree. "
    "A tree with N nodes has N-1 edges."
)

questions = [
    "What is a leaf node?",
    "How many edges does a tree with N nodes have?",
    "What is the time complexity of quick sort?",
]

for q in questions:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"NOTES:\n{paragraph}\n\nQUESTION: {q}"},
        ],
    )
    print("\nQ:", q)
    print("A:", response["message"]["content"])