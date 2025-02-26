import os
from dotenv import load_dotenv

load_dotenv()

class LocalSettings:
    def __init__(self):
        self.PARSED_CASES_DIR = "parsed_cases"
        self.EMBEDDINGS_DIR = os.path.join(self.PARSED_CASES_DIR, "embeddings")
        self.EMBEDDINGS_FILE = "embeddings.npy"
        self.METADATA_FILE = "metadata.npy"
        self.MILVUS_LOCAL_DIR = "milvus_local"
        self.MILVUS_DB_PATH = os.path.join(self.MILVUS_LOCAL_DIR, "milvus_oyez.db")
        self.COLLECTION_NAME = "oyez_cases"
        self.DIMENSION = 384
        self.TOP_K = 5
        self.MODEL_NAME = "all-MiniLM-L6-v2"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-1.5-flash"