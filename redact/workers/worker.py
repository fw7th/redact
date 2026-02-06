# model.py
import sys
import warnings

import torch
from gliner import GLiNER
from rq import Worker

from redact.core.redis import predict_queue, redis_conn

# sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")

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
ML_MODEL = GLiNER.from_pretrained(
    "/home/fw7th/redact/data/gliner_urchade/",
    local_files_only=True,
)

"""


def predict_entities(text, labels):
    return ML_MODEL.predict_entities(text, labels, threshold=0.28)


# Connect to Redis
if __name__ == "__main__":
    worker = Worker([predict_queue], connection=redis_conn)
    worker.work()
