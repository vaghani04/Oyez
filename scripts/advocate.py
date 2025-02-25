import os
import asyncio
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils
from scripts.utils.http_utils import HttpUtils
import json

class AdvocateProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.http_utils = HttpUtils()

    def validate_advocate(self, advocate_entry):
        if not isinstance(advocate_entry, dict) or "advocate" not in advocate_entry:
            return False
        advocate = advocate_entry.get("advocate", {})
        return isinstance(advocate, dict) and "href" in advocate and "identifier" in advocate

    def extract_advocate_metadata(self, advocate_details):
        fields = {
            "ID": None,
            "name": None,
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "identifier": None
        }
        for field in fields:
            fields[field] = advocate_details.get(field, fields[field])
        return fields

    async def fetch_and_store_image(self, session, image_url, image_path):
        image_data = await self.http_utils.fetch_binary(session, image_url)
        if image_data:
            self.file_utils.write_binary_file(image_path, image_data)

    async def process_advocate_images(self, session, advocate_details, images_dir):
        images = advocate_details.get("images", [])
        if not isinstance(images, list):
            return
        tasks = []
        for image_entry in images:
            if not isinstance(image_entry, dict) or "file" not in image_entry:
                continue
            file_info = image_entry.get("file", {})
            if not isinstance(file_info, dict) or "href" not in file_info:
                continue
            image_url = file_info.get("href")
            mime = file_info.get("mime", "image/jpeg")
            ext = mime.split("/")[-1] if mime else "jpg"
            advocate_name = advocate_details.get("identifier", "unknown")
            image_filename = f"{advocate_name}.{ext}"
            image_path = os.path.join(images_dir, image_filename)
            tasks.append(self.fetch_and_store_image(session, image_url, image_path))
        if tasks:
            await asyncio.gather(*tasks)

    async def process_advocate(self, session, advocate_entry, attorneys_dir):
        try:
            if not self.validate_advocate(advocate_entry):
                print(f"Skipping advocate: Invalid advocate data")
                return
            advocate = advocate_entry.get("advocate", {})
            advocate_href = advocate.get("href")
            advocate_details = await self.http_utils.fetch_json(session, advocate_href)
            if not isinstance(advocate_details, dict):
                print(f"Skipping advocate {advocate.get('identifier')}: Invalid details")
                return
            metadata = self.extract_advocate_metadata(advocate_details)
            attorneys_data = {metadata["identifier"]: metadata}
            details_path = os.path.join(attorneys_dir, self.settings.DETAILS_FILE)
            if os.path.exists(details_path):
                with open(details_path, "r") as f:
                    existing_data = json.load(f)
                existing_data.update(attorneys_data)
                attorneys_data = existing_data
            self.file_utils.write_json_file(details_path, attorneys_data)
            images_dir = os.path.join(attorneys_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            await self.process_advocate_images(session, advocate_details, images_dir)
        except Exception as e:
            print(f"Error processing advocate {advocate.get('identifier', 'unknown')}: {e}")

    async def process_advocates(self, session, advocates, case_dir):
        attorneys_dir = os.path.join(case_dir, self.settings.ATTORNEYS_DIR)
        self.file_utils.create_directory(attorneys_dir)
        tasks = []
        for advocate_entry in advocates:
            tasks.append(self.process_advocate(session, advocate_entry, attorneys_dir))
        if tasks:
            await asyncio.gather(*tasks)