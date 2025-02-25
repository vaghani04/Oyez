import os
import time
from rag.pinecone_cloud import PineconeCloudUpserter

class RagApp:
    def __init__(self):
        self.parsed_cases_dir = "parsed_cases"

    def upsert_to_pinecone(self):
        upserter = PineconeCloudUpserter()
        upserter.run()

    def run(self):
        start = time.time()
        print("Upserting to Pinecone...")
        self.upsert_to_pinecone()
        end = time.time()
        print(f"Total process completed in {(end-start):.2f} seconds")

if __name__ == "__main__":
    app = RagApp()
    app.run()