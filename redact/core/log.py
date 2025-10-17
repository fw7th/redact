"""
log.py
Logging functionality, saves log files too.
Author: fw7th
Date: 2025-04-25

modified (2025-10-16)
"""

import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # Set to DEBUG for detailed logs, ERROR for only failures
)

LOG = logging.getLogger(__name__)  # Best practice: use module name
LOG.setLevel(logging.DEBUG)

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging auto-creates log files
INFO_FILE = LOG_DIR / "info.log"
ERROR_FILE = LOG_DIR / "error.log"


# Create handlers
info_handler = logging.FileHandler(INFO_FILE)
error_handler = logging.FileHandler(ERROR_FILE)

info_handler.setLevel(logging.INFO)  # Info and above go here
error_handler.setLevel(logging.ERROR)  # Error and above go here

# Create formatters
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Also log to console during dev
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s [CONSOLE] %(message)s"))

# Add handlers to the logger
LOG.addHandler(info_handler)
LOG.addHandler(error_handler)
