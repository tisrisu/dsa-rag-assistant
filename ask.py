import sys
from pathlib import Path

import config
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv(config.BASE_DIR / ".env")
embedding = HuggingFaceEmbeddings(
    model_name=config.EMBEDDING_MODEL_NAME,
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = Chroma(
    collection_name=config.COLLECTION_NAME,
    embedding_function=embedding,
    persist_directory=str(config.CHROMA_DIR),
)

retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})

llm = ChatGroq(

    model_name=config.LLM_MODEL,
    temperature=0,
    max_tokens=1500,
    max_retries=2,
)



system_prompt = (

    "You are a helpful DSA assistant. Answer using ONLY the provided "
    "context, which contains C++ solutions to array problems. Each file "
    "is labeled with its source path. If the context does not contain "
    "enough information to answer the question, say clearly that you "
    "don't have a solution for that in the provided files — do not use "
    "outside knowledge or guess."
)


def load_original(doc):
    
    source = doc.metadata.get("source")
    if source:
        path = config.BASE_DIR / source
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            print(f"warning: could not read {source}, using stored text", file=sys.stderr)
    return doc.page_content


def format_context(docs):
    blocks = [
        f"File: {doc.metadata.get('source', 'Unknown')}\n{load_original(doc)}"
        for doc in docs
    ]
    return "\n\n".join(blocks)


def ask(query: str) -> str:
    
    docs = retriever.invoke(query)
    context = format_context(docs)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"context: {context}\n\n question: {query}"},
    ]

    response = llm.invoke(messages)

    return response.content


if __name__ == "__main__":

    question = " ".join(sys.argv[1:]) or "capital of france?"
    print(f"Q: {question}\n")
    print(ask(question))