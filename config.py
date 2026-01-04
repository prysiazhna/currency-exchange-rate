import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_CREDS_PATH = os.environ.get("GOOGLE_CREDS_PATH", "service-account.json")
GOOGLE_WORKSHEET_NAME = os.environ.get("GOOGLE_WORKSHEET_NAME", "exchange_rate")
API_TOKEN = os.environ.get("API_TOKEN", "dev_token")
