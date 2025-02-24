import os

class Settings:
    def __init__(self):
        self.START_YEAR = 2020
        self.END_YEAR = 2022
        self.BASE_URL = "https://api.oyez.org"
        self.PARSED_CASES_DIR = "parsed_cases"
        self.RESOLVED_DIR = os.path.join(self.PARSED_CASES_DIR, "Resolved")
        self.UNRESOLVED_DIR = os.path.join(self.PARSED_CASES_DIR, "UnResolved")