import os
import asyncio
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils
from scripts.utils.http_utils import HttpUtils

class ArgumentProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.http_utils = HttpUtils()

    def validate_oral_argument(self, oral_argument):
        if not isinstance(oral_argument, dict):
            return False
        return "href" in oral_argument

    def get_audio_url(self, media_files):
        if not isinstance(media_files, list):
            return None
        for media in media_files:
            if not isinstance(media, dict):
                continue
            if media.get("mime") == "audio/mpeg":
                return media.get("href")
        return None

    async def fetch_and_store_audio(self, session, audio_url, audio_path):
        audio_data = await self.http_utils.fetch_binary(session, audio_url)
        if audio_data:
            self.file_utils.write_binary_file(audio_path, audio_data)

    def generate_transcript(self, transcript):
        if not isinstance(transcript, dict) or "sections" not in transcript:
            return ""
        sections = transcript.get("sections", [])
        if not isinstance(sections, list):
            return ""
        transcript_text = []
        for section in sections:
            if not isinstance(section, dict) or "turns" not in section:
                continue
            turns = section.get("turns", [])
            if not isinstance(turns, list):
                continue
            for turn in turns:
                if not isinstance(turn, dict) or "speaker" not in turn or "text_blocks" not in turn:
                    continue
                speaker = turn.get("speaker", {})
                if not isinstance(speaker, dict) or "name" not in speaker:
                    continue
                speaker_name = speaker.get("name")
                text_blocks = turn.get("text_blocks", [])
                if not isinstance(text_blocks, list):
                    continue
                transcript_text.append(speaker_name)
                for block in text_blocks:
                    if not isinstance(block, dict) or "text" not in block:
                        continue
                    transcript_text.append(block.get("text"))
                transcript_text.append("")
                transcript_text.append("")
        return "\n".join(transcript_text).strip()

    async def process_argument_data(self, session, argument_details, argument_dir):
        try:
            if not isinstance(argument_details, dict):
                return
            audio_url = self.get_audio_url(argument_details.get("media_file", []))
            audio_path = os.path.join(argument_dir, self.settings.AUDIO_FILE)
            transcript_path = os.path.join(argument_dir, self.settings.TRANSCRIPT_FILE)
            tasks = []
            if audio_url:
                tasks.append(self.fetch_and_store_audio(session, audio_url, audio_path))
            transcript_text = self.generate_transcript(argument_details.get("transcript"))
            if transcript_text:
                self.file_utils.write_text_file(transcript_path, transcript_text)
            if tasks:
                await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error processing argument data: {e}")

    async def process_argument(self, session, oral_argument_audio, argument_dir):
        self.file_utils.create_directory(argument_dir)
        if not isinstance(oral_argument_audio, list) or not oral_argument_audio:
            return
        first_argument = oral_argument_audio[0]
        if not self.validate_oral_argument(first_argument):
            return
        argument_href = first_argument.get("href")
        argument_details = await self.http_utils.fetch_json(session, argument_href)
        await self.process_argument_data(session, argument_details, argument_dir)