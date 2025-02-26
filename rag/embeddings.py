import os
import numpy as np
from rag.settings import RagSettings
from rag.utils.embedding_utils import EmbeddingUtils
import json

class EmbeddingGenerator:
    def __init__(self, parsed_cases_dir):
        self.settings = RagSettings()
        self.parsed_cases_dir = parsed_cases_dir
        self.embedding_utils = EmbeddingUtils(self.settings.MODEL_NAME)

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
                    embedding = self.embedding_utils.generate_embedding(case_data, transcript_path)
                    embeddings.append(embedding)
                    metadata.append({"case_id": case_id, "case_dir": case_dir})
        
        embeddings_array = np.stack(embeddings)
        embeddings_dir = os.path.join(self.parsed_cases_dir, "embeddings")
        if not os.path.exists(embeddings_dir):
            os.makedirs(embeddings_dir)
        np.save(os.path.join(embeddings_dir, "embeddings.npy"), embeddings_array)
        np.save(os.path.join(embeddings_dir, "metadata.npy"), metadata, allow_pickle=True)