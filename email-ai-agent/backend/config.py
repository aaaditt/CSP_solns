from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SYNC_MAX_EMAILS = int(os.getenv("SYNC_MAX_EMAILS", "15"))
INCLUDE_BODY_SNIPPET = os.getenv("INCLUDE_BODY_SNIPPET", "true").strip().lower() == "true"
