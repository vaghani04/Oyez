import os
import numpy as np
from sentence_transformers import SentenceTransformer
import json

class EmbeddingGenerator:
    def __init__(self, parsed_cases_dir):
        self.parsed_cases_dir = parsed_cases_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # GPU if available

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

    def process_embeddings(self):
        embeddings = []
        metadata = []
        for root_dir in [os.path.join(self.parsed_cases_dir, "Resolved"), os.path.join(self.parsed_cases_dir, "UnResolved")]:
            if not os.path.exists(root_dir):
                continue
            for case_id in os.listdir(root_dir):
                case_dir = os.path.join(root_dir, case_id)
                if not os.path.isdir(case_dir):
                    continue
                case_json_path = os.path.join(case_dir, "case.json")
                transcript_path = os.path.join(case_dir, "argument", "transcript.txt")
                if os.path.exists(case_json_path):
                    with open(case_json_path, "r") as f:
                        case_data = json.load(f)
                    embedding = self.generate_embedding(case_data, transcript_path)
                    embeddings.append(embedding)
                    metadata.append({"case_id": case_id, "case_dir": case_dir})
        
        embeddings_array = np.stack(embeddings)
        embeddings_dir = os.path.join(self.parsed_cases_dir, "embeddings")
        if not os.path.exists(embeddings_dir):
            os.makedirs(embeddings_dir)
        np.save(os.path.join(embeddings_dir, "embeddings.npy"), embeddings_array)
        np.save(os.path.join(embeddings_dir, "metadata.npy"), metadata, allow_pickle=True)