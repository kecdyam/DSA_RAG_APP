import os

root = "DATA"

for folder, subfolders, files in os.walk(root):
    for filename in files:
        if filename.lower().endswith(".java"):
            path = os.path.join(folder, filename)
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            print(filename, "| lines:", text.count("\n") + 1, "| characters:", len(text))