import asyncio
import google.generativeai as genai
from rag.settings import RagSettings
from rag.retriever import PineconeRetriever
from rag.utils.llm_utils import LLMUtils

class LLMProcessor:
    def __init__(self):
        self.settings = RagSettings()
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.settings.GEMINI_MODEL)
        self.retriever = PineconeRetriever()
        self.llm_utils = LLMUtils()

    async def process_query(self, query):
        try:
            matches = await self.retriever.retrieve(query)
            if not matches:
                return {"response": "Sorry, I couldn't find any relevant cases for that query!"}
            parsed = self.llm_utils.parse_docs(matches)
            prompt_parts = self.llm_utils.build_prompt(parsed, query)
            response = await asyncio.to_thread(self.model.generate_content, prompt_parts)
            return {"response": response.text}
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            return {"response": "Oops! Something went wrong while fetching your answer."}

    async def run(self, query):
        result = await self.process_query(query)
        print(f"Response: {result['response']}")