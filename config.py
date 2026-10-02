from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data" / "Arrays"
FILE_GLOB = "*.cpp"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "arrays"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"  # max input 256 tokens
TOP_K = 3

CHUNK_SIZE = 200
CHUNK_OVERLAP = 20