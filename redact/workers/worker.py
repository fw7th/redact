# model.py
import sys
import warnings

import torch
from gliner import GLiNER

warnings.filterwarnings("ignore")

device = "cuda" if torch.cuda.is_available() else "cpu"
ML_MODEL = GLiNER.from_pretrained("urchade/gliner_medium-v2.1").to(
    device
)  # update to download model instead.


print("CUDA available:", torch.cuda.is_available())
print("CUDA device count:", torch.cuda.device_count())
print(
    "CUDA device name:",
    torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
)

"""
# For local downloaded model when doing dev.
ML_MODEL = GLiNER.from_pretrained(
    "/home/fw7th/redact/data/gliner_urchade/",
    local_files_only=True,
)
"""


def predict_entities(text, labels):
    return ML_MODEL.predict_entities(text, labels, threshold=0.28)
