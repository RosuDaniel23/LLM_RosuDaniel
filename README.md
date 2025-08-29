# Reading Bot (RAG + Tool Calling)

> Minimal educational project that shows how to combine an LLM with RAG (Retrieval-Augmented Generation) and a local tool/function call.

## Goal

This project was built to practice:
- **RAG** with a local **ChromaDB** vector store (not OpenAI vector store),
- **OpenAI Chat API** with **Function Calling**,
- A small **CLI** workflow end-to-end.

You ask for a type of book (e.g., "a book about freedom and control"); the system:
1) retrieves top matching books using **semantic search** (RAG),  
2) asks the LLM to recommend **exactly one** title from those candidates,  
3) automatically calls a local tool `get_summary_by_title(title)` to print the **full, detailed summary**.

---

## Features

- 12+ short book summaries are embedded with `text-embedding-3-small` and stored in **ChromaDB**.
- **CLI chatbot** that performs retrieval → model selection → function call for the detailed summary.
- Clear, small codebase for learning and reuse.

---

## Requirements

- Python **3.10+**
- An OpenAI API key available as environment variable `OPENAI_API_KEY`
- Internet connection (for embeddings & chat completions)

---


##  Quick Start

1. Clone the repository and set up the environment:
```bash
git clone https://github.com/<your-username>/smart-librarian.git
cd smart-librarian
python -m venv .venv
.venv\Scripts\activate    # On Windows
pip install -r requirements.txt
```

2. Add your OpenAI API key:
```bash
setx OPENAI_API_KEY "sk-..."   # Windows
# or export OPENAI_API_KEY="sk-..." on macOS/Linux
```

3. Build the index (creates embeddings and stores them in ChromaDB):
```bash
python build_index.py
```

4. Run the chatbot CLI:
```bash
python chat_cli.py
```

---

##  Example Usage

**Input**
```text
? Book search:
> I want a book about freedom and control
```

**Output**
```text
Recommended: 1984
Reason: It is a dystopian story focused on surveillance, truth, and social control.

Detailed Summary:
A society controlled by the Party, with total surveillance and propaganda.
Winston resists but is defeated through re-education.
```

 You can try other prompts like:
- `What do you recommend for someone who loves war stories?`
- `Recommend me something if I like fantasy adventures.`
- `What is The Hobbit?`

---

##  Project Structure

```bash
smart-librarian/
├── book_summaries.md   # Source list: 12+ books with Title, Themes, Short summary (for indexing)
├── summaries_dict.py   # Detailed summaries (used by the tool get_summary_by_title)
├── build_index.py      # Ingestion + embeddings + add to Chroma collection
├── chat_cli.py         # CLI: RAG + LLM + function calling
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

---

## ⚙️ How it works

1. **Indexing**: `build_index.py` → generates embeddings and stores them in ChromaDB.  
2. **Retrieval**: query embeddings → top-k matches from Chroma.  
3. **Recommendation**: Chat API chooses exactly one title.  
4. **Tool calling**: `get_summary_by_title` returns the detailed summary.

---
