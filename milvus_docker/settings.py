import os
from dotenv import load_dotenv

load_dotenv()

class DockerSettings:
    def __init__(self):
        self.PARSED_CASES_DIR = "parsed_cases"
        self.EMBEDDINGS_DIR = os.path.join(self.PARSED_CASES_DIR, "embeddings")
        self.EMBEDDINGS_FILE = "embeddings.npy"
        self.METADATA_FILE = "metadata.npy"
        self.MILVUS_HOST = "localhost"
        self.MILVUS_PORT = 19530
        self.COLLECTION_NAME = "oyez_cases_docker"
        self.DIMENSION = 384
        self.TOP_K = 5
        self.MODEL_NAME = "all-MiniLM-L6-v2"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-1.5-flash"
        self.MILVUS_URI = "http://localhost:19530"
        self.MILVUS_DB = "Oyez"