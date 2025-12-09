import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")
REDACT_BASE = os.getenv("REDACTED")
UPLOAD_BASE = os.getenv("UPLOADED")
PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)  # goes from core/config.py → project/


IMAGE_DIR = PROJECT_ROOT / BASE_DIR
REDACT_DIR = IMAGE_DIR / REDACT_BASE
UPLOAD_DIR = IMAGE_DIR / UPLOAD_BASE

print(PROJECT_ROOT)
