import config
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def main():
    # loading documents
    loader = DirectoryLoader(
        path=str(config.DATA_DIR),
        glob=config.FILE_GLOB,
        loader_cls=TextLoader,
    )
    docs = loader.load()
    print(f"loaded {len(docs)} files")

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

    ids = [doc.metadata["source"] for doc in docs]
    vectorstore.add_documents(docs, ids=ids)
    print(f"added {len(docs)} documents to vectorstore")
    print("ingestion complete")


if __name__ == "__main__":
    main()