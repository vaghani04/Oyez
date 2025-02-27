import os
from dotenv import load_dotenv

load_dotenv()

class DockerSettings:
    def __init__(self):
        self.PARSED_CASES_DIR = "parsed_cases"
        self.EMBEDDINGS_DIR = os.path.join(self.PARSED_CASES_DIR, "embeddings")
        self.EMBEDDINGS_FILE = "embeddings.npy"
        self.METADATA_FILE = "metadata.npy"
        self.PINECONE_URI = "http://localhost:5080"
        # self.INDEX_NAME = "oyez-cases-docker"
        self.INDEX_NAME = "index1"
        self.API_KEY = "pclocal"
        self.DIMENSION = 384
        self.TOP_K = 5
        self.MODEL_NAME = "all-MiniLM-L6-v2"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-1.5-flash"