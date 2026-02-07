# Run `modal deploy redact/workers/modelapp.py` from ~/redact/
from uuid import UUID

import modal

from redact.core.config import MODAL_APP
from redact.workers.inference import sync_full_inference

dockerfile_image = (
    modal.Image.debian_slim(python_version="3.10.16")
    .apt_install("tesseract-ocr-eng", "tesseract-ocr", "libgl1", "libglib2.0-0")
    .pip_install_from_requirements("modal-requirements.txt")
    .add_local_python_source("redact", ignore=["**/__pycache__", "*.pyc", ".venv"])
)

app = modal.App(MODAL_APP, image=dockerfile_image)


@app.function(
    concurrency_limit=1,
    allow_concurrent_inputs=False,
    gpu="T4",
    secrets=[modal.Secret.from_name("redact-secrets")],
)
def inference_work(batch_id: UUID):
    sync_full_inference(batch_id)
