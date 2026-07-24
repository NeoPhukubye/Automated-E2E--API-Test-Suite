import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://fakestoreapi.com")
UI_BASE_URL = os.getenv("UI_BASE_URL", "https://fakestoreapi.com")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
