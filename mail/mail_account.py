import os
from enum import StrEnum, auto

env_prefix = {
    "gmail": "GMAIL",
    "hotmail": "HOTMAIL"
}

class MailAccount:
    def __init__(self, account_type) -> None:       
        uvar = env_prefix.get(account_type.lower(), "EMAIL") 
        self.type = account_type
        self.password = db_url = os.environ[f"{uvar}_APP_PASSWORD"]
        self.username = db_url = os.environ[f"{uvar}_USERNAME"]