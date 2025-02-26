import asyncio
import numpy as np
from pymilvus import MilvusClient
from milvus_local.settings import LocalSettings
from rag.utils.embedding_utils import EmbeddingUtils

class MilvusLocalRetriever:
    def __init__(self):
        self.settings = LocalSettings()
        self.client = MilvusClient(self.settings.MILVUS_DB_PATH)
        self.embedding_utils = EmbeddingUtils(self.settings.MODEL_NAME)

    async def retrieve(self, query):
        try:
            query_embedding = self.embedding_utils.encode_query(query)
            self.client.load_collection(self.settings.COLLECTION_NAME)
            results = await asyncio.to_thread(
                self.client.search,
                collection_name=self.settings.COLLECTION_NAME,
                data=[query_embedding.tolist()],
                output_fields=["id", "case_dir"],
                limit=self.settings.TOP_K
            )
            matches = []
            for result in results[0]:
                matches.append({
                    "id": str(result["id"]),
                    "score": result["distance"],
                    "metadata": {"case_dir": result["entity"]["case_dir"]}
                })
            return matches
        except Exception as e:
            print(f"Error retrieving query '{query}': {e}")
            return []

    async def process_query(self, query):
        matches = await self.retrieve(query)
        if not matches:
            print("No matches found")
            return
        for match in matches:
            print(f"Case ID: {match['id']}, Score: {match['score']}, Metadata: {match['metadata']}")

    async def run(self, query):
        await self.process_query(query)