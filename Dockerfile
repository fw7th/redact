# 1. BASE IMAGE - Start with Python on Debian (has apt for installing tesseract)
FROM python:3.10-slim

# 2. INSTALL SYSTEM DEPENDENCIES
# - tesseract-ocr: the OCR engine
# - tesseract-ocr-eng: English language data (add more languages if needed)
# - libgl1: OpenCV dependency (your inference likely uses cv2)
# - libglib2.0-0: Another common image processing dependency
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# The rm command cleans up apt cache to keep image size smaller

# 3. SET WORKING DIRECTORY
# All subsequent commands run from here
WORKDIR /app

# 4. COPY REQUIREMENTS FIRST (optimization trick!)
# Why separate from code? If requirements.txt doesn't change,
# Docker reuses this cached layer even if code changes.
# This means faster rebuilds when you're just tweaking code.
COPY requirements.txt .

# 5. INSTALL PYTHON DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir keeps image smaller by not storing pip cache

# 6. COPY YOUR APPLICATION CODE
# This happens AFTER pip install so code changes don't invalidate pip cache
COPY redact/ ./redact/
COPY data/ ./data/

# 7. SET ENVIRONMENT VARIABLES (optional, can also set in Render dashboard)
# These tell Python not to buffer output (helps with logging)
ENV PYTHONUNBUFFERED=1

# 8. COMMAND TO RUN WHEN CONTAINER STARTS
# This runs your worker continuously
CMD ["python", "-m", "redact.workers.worker"]
