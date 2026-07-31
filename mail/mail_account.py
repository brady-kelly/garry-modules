import os
from enum import StrEnum, auto
from dotenv import load_dotenv

load_dotenv()

env_prefix = {
    "gmail": "GMAIL",
    "hotmail": "HOTMAIL",
    "outlook": "OUTLOOK"
}

class MailAccount:
    def __init__(self, account_type: str) -> None:     
        self.account_type = account_type.lower()
        vprefix = self.account_type.upper()
        self.password = os.environ[f"{vprefix}_APP_PASSWORD"] if self.account_type != "outlook" else None
        self.username = os.environ[f"{vprefix}_USERNAME"]