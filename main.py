import asyncio
import aiohttp
from scripts.settings import Settings
from scripts.utils.file_utils import FileUtils
from scripts.case import CaseProcessor

class CaseFetcher:
    def __init__(self):
        self.settings = Settings()
        self.file_utils = FileUtils()
        self.case_processor = CaseProcessor()

    async def fetch_cases_for_year(self, session, year):
        try:
            url = f"{self.settings.BASE_URL}/cases?per_page=0&filter=term:{year}"
            async with session.get(url) as response:
                return await response.json()
        except Exception as e:
            print(f"Error fetching cases for year {year}: {e}")
            return []

    def validate_year_response(self, cases):
        if not isinstance(cases, list):
            return False
        return True

    async def process_year(self, session, year):
        try:
            cases = await self.fetch_cases_for_year(session, year)
            if not cases or not self.validate_year_response(cases):
                print(f"Skipping year {year}: Invalid or missing case list")
                return
            tasks = []
            for case in cases:
                case_href = case.get("href")
                case_id = case.get("ID")
                # if case_id == 63187:  # This is for year 2020
                #     if not case_href or not case_id:
                #         print(f"Skipping case in year {year}: Missing href or id")
                #         continue
                #     tasks.append(self.case_processor.process_case(session, case_href, case_id))
                if not case_href or not case_id:
                    print(f"Skipping case in year {year}: Missing href or id")
                    continue
                tasks.append(self.case_processor.process_case(session, case_href, case_id))
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error processing year {year}: {e}")

    async def run(self):
        self.file_utils.create_directory(self.settings.PARSED_CASES_DIR)
        self.file_utils.create_directory(self.settings.RESOLVED_DIR)
        self.file_utils.create_directory(self.settings.UNRESOLVED_DIR)
        async with aiohttp.ClientSession() as session:
            year_tasks = []
            for year in range(self.settings.START_YEAR, self.settings.END_YEAR + 1):
                year_tasks.append(self.process_year(session, year))
            await asyncio.gather(*year_tasks)

if __name__ == "__main__":
    import time
    start = time.time()
    fetcher = CaseFetcher()
    asyncio.run(fetcher.run())
    end = time.time()
    print(f'Total Time: {(end-start):.2f}')