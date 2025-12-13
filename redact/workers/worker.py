# model.py
import os
import sys
import warnings

# sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")

# Suppress TensorFlow/CUDA warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TF warnings
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU search entirely
os.environ["JAX_PLATFORM_NAME"] = "cpu"
warnings.filterwarnings("ignore")

from gliner import GLiNER
from redis import Redis
from rq import Queue, Worker

from redact.core.redis import predict_queue, redis_conn

ML_MODEL = GLiNER.from_pretrained(
    "/home/fw7th/redact/data/gliner_urchade/",
    local_files_only=True,
)


def predict_entities(text, labels):
    return ML_MODEL.predict_entities(text, labels, threshold=0.28)


# Connect to Redis
if __name__ == "__main__":
    worker = Worker([predict_queue], connection=redis_conn)
    worker.work()
