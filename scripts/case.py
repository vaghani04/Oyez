import os
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils
from scripts.utils.http_utils import HttpUtils
from scripts.advocate import AdvocateProcessor
from scripts.member import MemberProcessor

class CaseProcessor:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.http_utils = HttpUtils()
        self.advocate_processor = AdvocateProcessor()
        self.member_processor = MemberProcessor()

    async def fetch_case_details(self, session, case_url):
            return await self.http_utils.fetch_json(session, case_url)
    
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
        if not isinstance(case_details, dict):
            return fields
        for field in fields:
            if field != "ID":
                fields[field] = case_details.get(field, fields[field])
        return fields

    async def process_case(self, session, case_href, case_id):
        try:
            case_details = await self.fetch_case_details(session, case_href)
            case_id_str = str(case_id)
            
            if not case_details or not self.validate_case_details(case_details):
                print(f"Skipping case {case_id}: Invalid or missing case details")
                return
            
            if not case_details or not self.validate_case_details(case_details):
                case_data = self.extract_case_data({})
                timeline = []
                advocates = []
                heard_by = []
                decided_by = []
            else:
                case_data = self.extract_case_data(case_details)
                timeline = case_details.get("timeline", [])
                advocates = case_details.get("advocates", [])
                heard_by = case_details.get("heard_by", [])
                decided_by = case_details.get("decided_by", [])

            is_resolved = self.is_case_resolved(timeline)
            if is_resolved:
                case_dir = os.path.join(self.settings.RESOLVED_DIR, case_id_str)
            else:
                case_dir = os.path.join(self.settings.UNRESOLVED_DIR, case_id_str)

            self.file_utils.create_directory(case_dir)
            self.file_utils.write_json_file(os.path.join(case_dir, "case.json"), case_data)
            
            # Attorneys Processing
            attorneys_dir = os.path.join(case_dir, self.settings.ATTORNEYS_DIR)
            self.file_utils.create_directory(attorneys_dir)
            images_dir = os.path.join(attorneys_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            details_path = os.path.join(attorneys_dir, self.settings.DETAILS_FILE)
            if not os.path.exists(details_path):
                self.file_utils.write_json_file(details_path, {})
            await self.advocate_processor.process_advocates(session, advocates, case_dir)

            # Members Processing
            members_dir = os.path.join(case_dir, self.settings.MEMBERS_DIR)
            self.file_utils.create_directory(members_dir)
            images_dir = os.path.join(members_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            details_path = os.path.join(members_dir, self.settings.DETAILS_FILE)
            if not os.path.exists(details_path):
                self.file_utils.write_json_file(details_path, {})
            await self.member_processor.process_members(session, heard_by, decided_by, case_dir)

        except Exception as e:
            case_id_str = str(case_id)
            if 'is_resolved' not in locals():
                is_resolved = False
            if is_resolved:
                case_dir = os.path.join(self.settings.RESOLVED_DIR, case_id_str)
            else:
                case_dir = os.path.join(self.settings.UNRESOLVED_DIR, case_id_str)
            
            attorneys_dir = os.path.join(case_dir, self.settings.ATTORNEYS_DIR)
            self.file_utils.create_directory(attorneys_dir)
            images_dir = os.path.join(attorneys_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            self.file_utils.write_json_file(os.path.join(attorneys_dir, self.settings.DETAILS_FILE), {})

            members_dir = os.path.join(case_dir, self.settings.MEMBERS_DIR)
            self.file_utils.create_directory(members_dir)
            images_dir = os.path.join(members_dir, self.settings.IMAGES_DIR)
            self.file_utils.create_directory(images_dir)
            self.file_utils.write_json_file(os.path.join(members_dir, self.settings.DETAILS_FILE), {})
            
            print(f"Processed case {case_id} with empty data due to error: {e}")