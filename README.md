# Smart Librarian (RAG + Tool Calling) — Minimal

## Ce face
- Indexează 12+ rezumate de cărți în **ChromaDB** folosind embeddings **OpenAI `text-embedding-3-small`**.
- Chat CLI care, la fiecare întrebare:
  1) face căutare semantică (RAG) în Chroma,
  2) cere modelului să aleagă *o singură* carte,
  3) **apelează un tool** `get_summary_by_title(title)` pentru a afișa rezumatul detaliat.

## Cerințe
- Python 3.10+
- Variabilă de mediu `OPENAI_API_KEY` setată

## Instalare
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
```

## 1) Construiește indexul
```bash
python build_index.py
```
Va crea un director `chroma_db/` cu colecția `books`.

## 2) Pornește chatbotul CLI
```bash
python chat_cli.py
```
Exemple de întrebări:
- `Vreau o carte despre libertate și control social.`
- `Ce recomanzi pentru cineva care iubește povești de război?`
- `Ce-mi recomanzi dacă iubesc poveștile fantastice?`

Tastează `q` pentru ieșire.

## Structură
```
smart-librarian/
├─ book_summaries.md          # 12+ cărți (titlu, teme, scurt rezumat) – sursa pentru index
├─ summaries_dict.py          # rezumate detaliate folosite de tool
├─ build_index.py             # ingestion + embeddings + indexing în Chroma
├─ chat_cli.py                # chat + RAG + tool calling
├─ requirements.txt
└─ README.md
```

## Notă
- Folosește **Chroma** (nu OpenAI vector store), conform cerinței.
- Tool-ul este înregistrat în Chat API și apelat automat după recomandare.
- Poți modifica/adauga cărți editând `book_summaries.md` și `summaries_dict.py` apoi rulând din nou `build_index.py`.
