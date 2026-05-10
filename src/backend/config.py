import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
TEXTBOOK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "textbooks")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PRELOADED_TEXTS_DIR = os.path.join(PROJECT_ROOT, "extracted_texts")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEXTBOOK_DATA_DIR, exist_ok=True)
