import asyncio
from pinecone.grpc import PineconeGRPC as Pinecone
from rag.settings import RagSettings
from rag.utils.embedding_utils import EmbeddingUtils

class PineconeRetriever:
    def __init__(self):
        self.settings = RagSettings()
        self.pc = Pinecone(api_key=self.settings.PINECONE_API_KEY)
        self.index = self.pc.Index(self.settings.PINECONE_INDEX_NAME)
        self.embedding_utils = EmbeddingUtils(self.settings.MODEL_NAME)

    async def retrieve(self, query):
        try:
            query_embedding = self.embedding_utils.encode_query(query)
            results = await asyncio.to_thread(
                self.index.query,
                namespace=self.settings.PINECONE_NAMESPACE,
                vector=query_embedding.tolist(),
                top_k=self.settings.TOP_K,
                include_metadata=True
            )
            return results.get("matches", [])
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