import os, re, json
from openai import OpenAI
import chromadb

BOOKS_MD = "book_summaries.md"
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "books"

def parse_books_md(path: str):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    pattern = r"##\s*Title:\s*(.+?)\nThemes:\s*(.+?)\nSummary:\s*([\s\S]*?)(?=\n##\s*Title:|\Z)"
    matches = re.findall(pattern, txt)
    items = []
    for (title, themes, summary) in matches:
        items.append({
            "title": title.strip(),
            "themes": [t.strip() for t in themes.split(",") if t.strip()],
            "summary": summary.strip()
        })
    return items

def embed_texts(client: OpenAI, texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY first.")
    client = OpenAI(api_key=api_key)

    items = parse_books_md(BOOKS_MD)
    if not items:
        raise SystemExit("No books parsed from book_summaries.md")

    chroma = chromadb.PersistentClient(path=PERSIST_DIR)
    try:
        col = chroma.get_collection(COLLECTION_NAME)
        chroma.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    col = chroma.get_or_create_collection(COLLECTION_NAME)

    docs = [it["summary"] for it in items]
    embeddings = embed_texts(client, docs)
    ids = [f"book-{i+1}" for i in range(len(items))]
    metadatas = [{"title": it["title"], "themes": it["themes"]} for it in items]

    col.add(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)
    print(f"Indexed {len(items)} books into Chroma at '{PERSIST_DIR}' in collection '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    main()
