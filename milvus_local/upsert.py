import numpy as np
from pymilvus import MilvusClient
from milvus_local.settings import LocalSettings
import os

class MilvusLocalUpserter:
    def __init__(self):
        self.settings = LocalSettings()
        self.client = MilvusClient(self.settings.MILVUS_DB_PATH)

    def load_embeddings(self):
        embeddings_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.EMBEDDINGS_FILE)
        metadata_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.METADATA_FILE)
        try:
            embeddings = np.load(embeddings_path)
            metadata = np.load(metadata_path, allow_pickle=True)
            return embeddings, metadata
        except Exception as e:
            print(f"Failed to load embeddings or metadata: {e}")
            return None, None

    def upsert(self):
        embeddings, metadata = self.load_embeddings()
        if embeddings is None or metadata is None:
            print("No embeddings to upsert")
            return
        
        valid_indices = [i for i, emb in enumerate(embeddings) if not np.all(emb == 0)]
        if not valid_indices:
            print("No valid embeddings to upsert")
            return
        embeddings = embeddings[valid_indices].astype('float32')
        metadata = metadata[valid_indices]
        
        data = [
            {
                "id": int(meta["case_id"]),
                "vector": emb.tolist(),
                "case_dir": meta["case_dir"]
            }
            for emb, meta in zip(embeddings, metadata)
        ]
        
        if self.client.has_collection(self.settings.COLLECTION_NAME):
            self.client.drop_collection(self.settings.COLLECTION_NAME)
        self.client.create_collection(
            collection_name=self.settings.COLLECTION_NAME,
            dimension=self.settings.DIMENSION
        )
        
        res = self.client.insert(
            collection_name=self.settings.COLLECTION_NAME,
            data=data
        )
        print(f"Upsert result: {res}")

    def run(self):
        self.upsert()

if __name__ == "__main__":
    upserter = MilvusLocalUpserter()
    upserter.run()