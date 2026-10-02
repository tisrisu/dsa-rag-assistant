import config
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma



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

retriver = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K}) 

docs = retriver.invoke("rotate an array")

for doc in docs:
    print(doc.metadata["source"])
    print(doc.page_content)
    