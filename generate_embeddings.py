import os
import time
from rag.embeddings import EmbeddingGenerator

class EmbeddingCreator:
    def __init__(self):
        self.parsed_cases_dir = "parsed_cases"

    def run(self):
        start = time.time()
        print("Generating embeddings...")
        embedding_generator = EmbeddingGenerator(self.parsed_cases_dir)
        embedding_generator.process_embeddings()
        end = time.time()
        print(f"Embedding generation completed in {(end-start):.2f} seconds")

if __name__ == "__main__":
    creator = EmbeddingCreator()
    creator.run()