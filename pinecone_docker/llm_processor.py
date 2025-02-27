import asyncio
import google.generativeai as genai
from pinecone_docker.settings import DockerSettings
from pinecone_docker.retriever import PineconeDockerRetriever
from rag.utils.llm_utils import LLMUtils

class PineconeDockerLLMProcessor:
    def __init__(self):
        self.settings = DockerSettings()
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.settings.GEMINI_MODEL)
        self.retriever = PineconeDockerRetriever()
        self.llm_utils = LLMUtils()

    async def process_query(self, query):
        try:
            matches = await self.retriever.retrieve(query)
            if not matches:
                return {"response": "Sorry, I couldn't find any relevant cases for that query in Pinecone Docker!"}
            parsed = self.llm_utils.parse_docs(matches)
            prompt_parts = self.llm_utils.build_prompt(parsed, query)
            response = await asyncio.to_thread(self.model.generate_content, prompt_parts)
            scores = [{"id": match["id"], "score": match["score"]} for match in matches]
            return {"response": response.text, "scores": scores}
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            return {"response": "Oops! Something went wrong while fetching your answer from Pinecone Docker."}

    async def run(self, query):
        result = await self.process_query(query)
        print(f"Response: {result['response']}")