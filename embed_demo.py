from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

sentences = [
    "A tree has a root node and child nodes.",
    "The topmost node of a hierarchy is called the root.",
    "An array stores elements at numbered positions.",
    "I like eating pizza on weekends.",
]

question = "What is the first node in a tree called?"

sentence_vectors = model.encode(sentences)
question_vector = model.encode(question)

scores = util.cos_sim(question_vector, sentence_vectors)[0]

for sentence, score in zip(sentences, scores):
    print(round(float(score), 3), "|", sentence)