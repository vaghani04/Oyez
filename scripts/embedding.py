import os
import numpy as np
import aiofiles
import asyncio
from sentence_transformers import SentenceTransformer
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils

class EmbeddingProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def split_text(self, text, max_length=400):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def generate_embedding(self, case_data, transcript_path):
        text_parts = []
        if isinstance(case_data.get("facts_of_the_case"), str):
            text_parts.append(case_data["facts_of_the_case"])
        if isinstance(case_data.get("conclusion"), str):
            text_parts.append(case_data["conclusion"])
        if os.path.exists(transcript_path):
            with open(transcript_path, "r") as f:
                text_parts.append(f.read())
        full_text = " ".join(text_parts)
        if not full_text.strip():
            return np.zeros(384)
        chunks = self.split_text(full_text)
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        return np.mean(embeddings, axis=0)

    async def save_embedding_async(self, embedding_path, embedding):
        async with aiofiles.open(embedding_path, "wb") as f:
            await f.write(np.asarray(embedding).tobytes())
            await f.flush()

    async def process_embedding_async(self, case_dir, case_data, case_id):
        embeddings_dir = os.path.join(case_dir, self.settings.EMBEDDINGS_DIR)
        self.file_utils.create_directory(embeddings_dir)
        transcript_path = os.path.join(case_dir, self.settings.ARGUMENT_DIR, self.settings.TRANSCRIPT_FILE)
        embedding = self.generate_embedding(case_data, transcript_path)
        embedding_path = os.path.join(embeddings_dir, self.settings.EMBEDDING_FILE(case_id))
        await self.save_embedding_async(embedding_path, embedding)

    def process_embedding_wrapper(self, args):
        case_dir, case_data, case_id = args
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process_embedding_async(case_dir, case_data, case_id))
        loop.close()