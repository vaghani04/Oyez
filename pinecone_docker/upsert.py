import numpy as np
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import ServerlessSpec
from pinecone_docker.settings import DockerSettings
import os
import time

class PineconeDockerUpserter:
    def __init__(self):
        self.settings = DockerSettings()
        self.pc = PineconeGRPC(
            api_key=self.settings.API_KEY,
            host=self.settings.PINECONE_URI
        )

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

        # if not self.pc.has_index(self.settings.INDEX_NAME):
        try:
            self.pc.create_index(
                name=self.settings.INDEX_NAME,
                dimension=self.settings.DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        except Exception as e:
            print(f"Index creation skipped (might already exist): {e}")

        while not self.pc.describe_index(self.settings.INDEX_NAME).status['ready']:
            time.sleep(1)

        index_host = self.pc.describe_index(self.settings.INDEX_NAME).host
        index = self.pc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))

        vectors = [
            (meta["case_id"], emb.tolist(), {"case_dir": meta["case_dir"]})
            for emb, meta in zip(embeddings, metadata)
        ]
        index.upsert(vectors=vectors, namespace="oyez-docker")
        print(f"Upsert completed for {len(vectors)} vectors")

    def run(self):
        self.upsert()

if __name__ == "__main__":
    upserter = PineconeDockerUpserter()
    upserter.run()