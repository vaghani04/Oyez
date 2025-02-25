import asyncio
import numpy as np
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from rag.settings import RagSettings
import os

class PineconeCloudUpserter:
    def __init__(self):
        self.settings = RagSettings()
        self.pc = Pinecone(api_key=self.settings.PINECONE_API_KEY)
        if not self.pc.has_index(self.settings.PINECONE_INDEX_NAME):
            self.pc.create_index(
                name=self.settings.PINECONE_INDEX_NAME,
                dimension=self.settings.PINECONE_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=self.settings.PINECONE_CLOUD,
                    region=self.settings.PINECONE_REGION
                )
            )
        while not self.pc.describe_index(self.settings.PINECONE_INDEX_NAME).status['ready']:
            asyncio.sleep(1)
        self.index = self.pc.Index(self.settings.PINECONE_INDEX_NAME)

    async def load_embeddings(self):
        embeddings_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.EMBEDDINGS_FILE)
        metadata_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.METADATA_FILE)
        try:
            embeddings = np.load(embeddings_path)
            metadata = np.load(metadata_path, allow_pickle=True)
            return embeddings, metadata
        except Exception as e:
            print(f"Failed to load embeddings or metadata: {e}")
            return None, None

    async def upsert_batch(self, vectors):
        try:
            await asyncio.to_thread(
                self.index.upsert,
                vectors=vectors,
                namespace=self.settings.PINECONE_NAMESPACE
            )
        except Exception as e:
            print(f"Error upserting batch: {e}")

    async def process_upsert(self):
        embeddings, metadata = await self.load_embeddings()
        if embeddings is None or metadata is None:
            print("No embeddings to upsert")
            return
        
        valid_indices = [i for i, emb in enumerate(embeddings) if not np.all(emb == 0)]
        if not valid_indices:
            print("No valid embeddings to upsert")
            return
        embeddings = embeddings[valid_indices]
        metadata = metadata[valid_indices]
        
        tasks = []
        for i in range(0, len(embeddings), self.settings.BATCH_SIZE):
            batch_embeddings = embeddings[i:i + self.settings.BATCH_SIZE]
            batch_metadata = metadata[i:i + self.settings.BATCH_SIZE]
            vectors = [
                {
                    "id": meta["case_id"],
                    "values": emb.tolist(),
                    "metadata": {"case_dir": meta["case_dir"]}
                }
                for emb, meta in zip(batch_embeddings, batch_metadata)
            ]
            tasks.append(self.upsert_batch(vectors))
        
        if tasks:
            await asyncio.gather(*tasks)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_upsert())