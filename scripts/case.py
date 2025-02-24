import os
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils

class CaseProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()

    async def fetch_case_details(self, session, case_url):
        try:
            async with session.get(case_url) as response:
                return await response.json()
        except Exception as e:
            print(f"Failed to fetch case details from {case_url}: {e}")
            return None

    def validate_case_details(self, case_details):
        if not isinstance(case_details, dict):
            return False
        required_keys = ["ID", "timeline"]
        return all(key in case_details for key in required_keys)

    def is_case_resolved(self, timeline):
        if not isinstance(timeline, list):
            return False
        for event in timeline:
            if not isinstance(event, dict) or "event" not in event:
                continue
            if event.get("event") == "Decided":
                return True
        return False

    def extract_case_data(self, case_details):
        fields = {
            "ID": None,
            "name": None,
            "docket_number": None,
            "term": None,
            "timeline": [],
            "facts_of_the_case": None,
            "conclusion": None,
            "citation": None,
            "lower_court": None
        }
        for field in fields:
            fields[field] = case_details.get(field, fields[field])
        return fields

    async def process_case(self, session, case_href, case_id):
        try:
            case_details = await self.fetch_case_details(session, case_href)
            if not case_details or not self.validate_case_details(case_details):
                print(f"Skipping case {case_id}: Invalid or missing case details")
                return
            timeline = case_details.get("timeline", [])
            is_resolved = self.is_case_resolved(timeline)
            case_data = self.extract_case_data(case_details)
            case_id = str(case_id)
            if is_resolved:
                case_dir = os.path.join(self.settings.RESOLVED_DIR, case_id)
            else:
                case_dir = os.path.join(self.settings.UNRESOLVED_DIR, case_id)
            self.file_utils.create_directory(case_dir)
            self.file_utils.write_json_file(os.path.join(case_dir, "case.json"), case_data)
        except Exception as e:
            print(f"Error processing case {case_id}: {e}")