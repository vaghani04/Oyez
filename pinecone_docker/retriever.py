import asyncio
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone_docker.settings import DockerSettings
from rag.utils.embedding_utils import EmbeddingUtils

class PineconeDockerRetriever:
    def __init__(self):
        self.settings = DockerSettings()
        self.pc = PineconeGRPC(
            api_key=self.settings.API_KEY,
            host=self.settings.PINECONE_URI
        )
        index_host = self.pc.describe_index(self.settings.INDEX_NAME).host
        self.index = self.pc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))
        self.embedding_utils = EmbeddingUtils(self.settings.MODEL_NAME)

    async def retrieve(self, query):
        try:
            query_embedding = self.embedding_utils.encode_query(query)
            results = await asyncio.to_thread(
                self.index.query,
                vector=query_embedding.tolist(),
                top_k=self.settings.TOP_K,
                include_metadata=True,
                namespace="oyez-docker"
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
    # async def run(self):
    #     query = "Crime Cases"
        await self.process_query(query)
        print("HEY, THIS IS PINECONE DOCKER")

# if __name__ == "__main__":
#     upserter = PineconeDockerRetriever()
#     upserter.run()