import os
from dotenv import load_dotenv

load_dotenv()

class RagSettings:
    def __init__(self):
        self.PARSED_CASES_DIR = "parsed_cases"
        self.EMBEDDINGS_DIR = os.path.join(self.PARSED_CASES_DIR, "embeddings")
        self.EMBEDDINGS_FILE = "embeddings.npy"
        self.METADATA_FILE = "metadata.npy"
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_CLOUD = os.getenv("PINECONE_CLOUD")
        self.PINECONE_REGION = os.getenv("PINECONE_REGION")
        self.PINECONE_INDEX_NAME = "oyez-cases"
        self.PINECONE_NAMESPACE = "oyez-namespace"
        self.PINECONE_DIMENSION = 384
        self.BATCH_SIZE = 100
        self.TOP_K = 5
        self.MODEL_NAME = "all-MiniLM-L6-v2"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-1.5-flash"