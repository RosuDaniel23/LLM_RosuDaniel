import os, json, textwrap
from typing import List, Dict, Any
from openai import OpenAI
import chromadb
from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Prompt
from summaries_dict import BOOK_SUMMARIES

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "books"
MODEL = "gpt-4o-mini"

def get_summary_by_title(title: str) -> str:
    return BOOK_SUMMARIES.get(title, "Nu am gasit un rezumat detaliat pentru acest titlu.")

def format_candidates(titles, docs, metadatas):
    lines = []
    for i, (t, doc, meta) in enumerate(zip(titles, docs, metadatas), start=1):
        themes = ", ".join(meta.get("themes", []))
        snippet = doc.strip().replace("\n", " ")
        snippet = (snippet[:280] + "…") if len(snippet) > 280 else snippet
        lines.append(f"""[{i}] Title: {t}\nThemes: {themes}\nSnippet: {snippet}""")
    return "\n\n".join(lines)

def retrieve(client_chroma, query: str, n_results: int = 5):
    col = client_chroma.get_collection(COLLECTION_NAME)
    oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    q_emb = oai.embeddings.create(model="text-embedding-3-small", input=[query]).data[0].embedding
    res = col.query(query_embeddings=[q_emb], n_results=n_results, include=["documents", "metadatas"])
    titles = [m.get("title", "Unknown") for m in res["metadatas"][0]]
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return titles, docs, metas

def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in environment before running.")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chroma = chromadb.PersistentClient(path=PERSIST_DIR)
    try:
        chroma.get_collection(COLLECTION_NAME)
    except Exception as e:
        raise SystemExit("Nu exista index. Ruleaza mai intai: python build_index.py")

    system_prompt = """Esti Smart Librarian, un asistent care recomanda O SINGURA carte din candidatii oferiti.
- Alege titlul care potriveste cel mai bine interesul utilizatorului.
- Raspunde concis in romana.
- Formatul raspunsului:
Recommendation: <Titlu exact>
Why: <o fraza de justificare>
Apoi cheama tool-ul get_summary_by_title cu titlul exact recomandat pentru a afisa un rezumat detaliat.
IMPORTANT: Titlul trebuie sa fie EXACT unul din lista de candidati.
"""

    tools = [{
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Returneaza rezumatul detaliat pentru un titlu exact de carte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titlul exact al cartii selectate."}
                },
                "required": ["title"]
            }
        }
    }]

    rprint(Panel.fit("[bold]Smart Librarian[/bold] – tasteaza intrebarea ta (q pentru iesire)"))
    while True:
        query = Prompt.ask("[cyan]Tu[/cyan]")
        if not query or query.strip().lower() in {"q", "quit", "exit"}:
            break

        titles, docs, metas = retrieve(chroma, query, n_results=5)
        candidates = format_candidates(titles, docs, metas)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Interesul utilizatorului: {query}\n\nCandidati:\n{candidates}"}
        ]

        first = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
        )

        msg = first.choices[0].message
        messages.append({"role":"assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})

        if msg.tool_calls:
            for call in msg.tool_calls:
                if call.function.name == "get_summary_by_title":
                    try:
                        args = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    title = args.get("title", "")
                    tool_result = get_summary_by_title(title)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": tool_result
                    })

            final = client.chat.completions.create(model=MODEL, messages=messages, temperature=0)
            rprint(Panel(final.choices[0].message.content, title="Smart Librarian"))
        else:
            rprint(Panel(msg.content or "(fara continut)", title="Smart Librarian"))

if __name__ == "__main__":
    main()
