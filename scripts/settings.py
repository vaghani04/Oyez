import os

class Settings:
    def __init__(self):
        self.START_YEAR = 1990
        self.END_YEAR = 1994
        self.BASE_URL = "https://api.oyez.org"
        self.PARSED_CASES_DIR = "parsed_cases"
        # self.PARSED_CASES_DIR = "parsed_cases_2"
        self.RESOLVED_DIR = os.path.join(self.PARSED_CASES_DIR, "Resolved")
        self.UNRESOLVED_DIR = os.path.join(self.PARSED_CASES_DIR, "UnResolved")
        self.ATTORNEYS_DIR = "attorneys"
        self.MEMBERS_DIR = "members"
        self.ARGUMENT_DIR = "argument"
        self.IMAGES_DIR = "images"
        self.DETAILS_FILE = "details.json"
        self.AUDIO_FILE = "audio.mp3"
        self.TRANSCRIPT_FILE = "transcript.txt"