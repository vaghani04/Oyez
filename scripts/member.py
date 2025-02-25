import os
import asyncio
import json
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils
from scripts.utils.http_utils import HttpUtils

class MemberProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.http_utils = HttpUtils()

    def validate_member(self, member):
        if not isinstance(member, dict):
            return False
        return "href" in member and "identifier" in member

    def extract_member_metadata(self, member_details):
        fields = {
            "ID": None,
            "name": None,
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "identifier": None,
            "roles": [],
            "law_school": None,
            "home_state": None
        }
        if not isinstance(member_details, dict):
            return fields
        for field in fields:
            fields[field] = member_details.get(field, fields[field])
        return fields

    async def fetch_and_store_image(self, session, image_url, image_path):
        image_data = await self.http_utils.fetch_binary(session, image_url)
        if image_data:
            self.file_utils.write_binary_file(image_path, image_data)

    async def process_member_images(self, session, member_details, images_dir):
        images = member_details.get("images", [])
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
            member_name = member_details.get("identifier", "unknown")
            image_filename = f"{member_name}.{ext}"
            image_path = os.path.join(images_dir, image_filename)
            tasks.append(self.fetch_and_store_image(session, image_url, image_path))
        if tasks:
            await asyncio.gather(*tasks)

    async def process_member(self, session, member, members_dir):
        try:
            if not self.validate_member(member):
                return
            member_href = member.get("href")
            member_details = await self.http_utils.fetch_json(session, member_href)
            if not isinstance(member_details, dict):
                return
            metadata = self.extract_member_metadata(member_details)
            members_data = {metadata["identifier"]: metadata}
            details_path = os.path.join(members_dir, self.settings.DETAILS_FILE)
            if os.path.exists(details_path):
                with open(details_path, "r") as f:
                    existing_data = json.load(f)
                existing_data.update(members_data)
                members_data = existing_data
            self.file_utils.write_json_file(details_path, members_data)
            images_dir = os.path.join(members_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            await self.process_member_images(session, member_details, images_dir)
        except Exception as e:
            print(f"Error processing member {member.get('identifier', 'unknown')}: {e}")

    async def process_member_group(self, session, group, members_dir):
        if not isinstance(group, list):
            return
        tasks = []
        seen_identifiers = set()
        for court in group:
            if not isinstance(court, dict) or "members" not in court:
                continue
            members = court.get("members", [])
            if not isinstance(members, list):
                continue
            for member in members:
                if not self.validate_member(member):
                    continue
                identifier = member.get("identifier")
                if identifier in seen_identifiers:
                    continue
                seen_identifiers.add(identifier)
                tasks.append(self.process_member(session, member, members_dir))
        if tasks:
            await asyncio.gather(*tasks)

    async def process_members(self, session, heard_by, decided_by, case_dir):
        members_dir = os.path.join(case_dir, self.settings.MEMBERS_DIR)
        self.file_utils.create_directory(members_dir)
        images_dir = os.path.join(members_dir, self.settings.IMAGES_DIR)
        self.file_utils.create_directory(images_dir)
        details_path = os.path.join(members_dir, self.settings.DETAILS_FILE)
        if not os.path.exists(details_path):
            self.file_utils.write_json_file(details_path, {})
        await asyncio.gather(
            self.process_member_group(session, heard_by, members_dir),
            self.process_member_group(session, decided_by, members_dir)
        )