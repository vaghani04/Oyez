import os
import time
import asyncio
from rag.pinecone_cloud import PineconeCloudUpserter
from rag.retriever import PineconeRetriever
from rag.llm_processor import LLMProcessor

class RagApp:
    def __init__(self):
        self.parsed_cases_dir = "parsed_cases"

    def upsert_to_pinecone(self):
        upserter = PineconeCloudUpserter()
        upserter.run()

    async def retrieve_from_pinecone(self, query):
        retriever = PineconeRetriever()
        await retriever.run(query)

    async def process_with_llm(self, query):
        processor = LLMProcessor()
        await processor.run(query)

    async def run(self):
        start = time.time()
        
        # print("Upserting to Pinecone...")
        # self.upsert_to_pinecone()
        
        # print("Retrieving from Pinecone...")
        # await self.retrieve_from_pinecone("tax disputes")
        
        print("Processing with LLM...")
        await self.process_with_llm("What are the key points about tax disputes?")

        end = time.time()
        print(f"Total process completed in {(end-start):.2f} seconds")

if __name__ == "__main__":
    app = RagApp()
    asyncio.run(app.run())