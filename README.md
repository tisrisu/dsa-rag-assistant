# DSA RAG Assistant

A small question-answering assistant over 40 of my C++ solutions to array problems. You ask a question in plain English, it finds the most relevant solution files, and an LLM answers using only those files.

## How it works
1. `ingest.py` reads the 40 `.cpp` files in `data/Arrays`, embeds them with BAAI/bge-small-en-v1.5 and stores them in a local Chroma database (`chroma_db`).
2. `ask.py` embeds the question, takes the top 3 files and sends the original file text to an LLM on Groq (`openai/gpt-oss-120b`).
3. If the files don't contain a solution, the assistant says so instead of guessing.

The text that gets embedded depends on `INDEX_VARIANT` (an environment variable, default `title`). `title` adds a title made from the file name to the file text. The other variants are `raw`, `strip` and `strip_title`. The LLM always sees the original file, never the changed text.

## Setup (Windows)
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

Create a `.env` file in the project folder with your Groq key:

    GROQ_API_KEY=your_key_here

## Run
    python ingest.py
    python ask.py "merge overlapping intervals"

## Measuring retrieval
`eval_retrieval.py` scores how often the right file is found for 17 questions (and 5 held-out questions). It reports hit@1, hit@3, hit@10 and MRR.

    python eval_retrieval.py --label my-run

Each run is added to `eval_log.csv` (summary) and `eval_details.csv` (per question). `python compare.py <label> <label>` shows ranks side by side. `run_variants.ps1` rebuilds the index and scores all four variants (pass the path of your python with `-py`).

## Result of Experiment A
I tested four ways of building the text that gets embedded. The predictions were committed before any run.

| variant | hit@1 | hit@3 | hit@10 |
|---|---|---|---|
| raw (baseline) | 47.1% | 52.9% | 82.4% |
| title | 52.9% | 76.5% | 88.2% |
| strip | 29.4% | 52.9% | 82.4% |
| strip + title | 52.9% | 70.6% | 94.1% |

I use `title`. On the 5 held-out questions, title got 4 of 5 in the top 3 and raw got 3 of 5. The full notes, including a mistake with labels and how I redid the runs, are in `EXPERIMENTS.md`.

## Limits
- It only answers from the 40 files. For anything else it says it has no solution.
- The test sets are small (17 + 5 questions). I wrote the 17 while looking at the file names, so the gain from `title` may be overstated.
- Four of the 17 questions still miss the top 3 (single number, leaders in an array, majority element n/2 and n/3).
- The LLM sometimes adds its own comments to the code when it explains it.

## Files
- `ingest.py`, `ask.py`, `config.py`, `textprep.py`: build the index and answer questions
- `eval_retrieval.py`, `eval_set.py`, `compare.py`, `run_variants.ps1`: the benchmark
- `EXPERIMENTS.md`: the experiment notes