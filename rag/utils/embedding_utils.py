import numpy as np
from sentence_transformers import SentenceTransformer
import os

class EmbeddingUtils:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def encode_query(self, query):
        return self.model.encode(query, show_progress_bar=False)

    def split_text(self, text, max_length=400):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def generate_embedding(self, case_data, transcript_path):
        text_parts = []
        if isinstance(case_data.get("facts_of_the_case"), str):
            text_parts.append(case_data["facts_of_the_case"])
        if isinstance(case_data.get("conclusion"), str):
            text_parts.append(case_data["conclusion"])
        if os.path.exists(transcript_path):
            with open(transcript_path, "r") as f:
                text_parts.append(f.read())
        full_text = " ".join(text_parts)
        if not full_text.strip():
            return np.zeros(384)
        chunks = self.split_text(full_text)
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        return np.mean(embeddings, axis=0)