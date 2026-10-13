import os 
import config
from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from textprep import build_index_text

def main():
    # loading documents
    loader = DirectoryLoader(
        path=str(config.DATA_DIR),
        glob=config.FILE_GLOB,
        loader_cls=TextLoader,
    )
    docs = loader.load()
    print(f"loaded {len(docs)} files")

    index_docs = [
        Document(
            page_content=build_index_text(
                os.path.basename(doc.metadata["source"]),
                doc.page_content,
                config.INDEX_VARIANT,
            ),
            metadata={**doc.metadata, "index_variant" : config.INDEX_VARIANT},
        )
        for doc in docs
    ]
    avg_len = sum(len(d.page_content) for d in index_docs) // len(index_docs)
    print(f"variant: {config.INDEX_VARIANT} | average embedded text: {avg_len} characters")

    # embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(config.CHROMA_DIR),
    )

    existing = len(vectorstore.get()["ids"])
    if existing:
        raise SystemExit(
            f"chroma_db already holds {existing} documents."
            "Delete the folder first so the index contains exactly one variant."
        )


    ids = [doc.metadata["source"] for doc in index_docs]
    vectorstore.add_documents(index_docs, ids=ids)
    print(f"added {len(index_docs)} documents to vectorstore")
    print("ingestion complete")


if __name__ == "__main__":
    main()