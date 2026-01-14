# model.py
import os
import warnings

from gliner import GLiNER
from rq import Worker

from redact.core.redis import predict_queue, redis_conn

# Suppress TensorFlow/CUDA warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TF warnings
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU search entirely
os.environ["JAX_PLATFORM_NAME"] = "cpu"
warnings.filterwarnings("ignore")

ML_MODEL = GLiNER.from_pretrained(
    "urchade/gliner_medium-v2.1"
)  # update to download model instead.


def predict_entities(text, labels):
    return ML_MODEL.predict_entities(text, labels, threshold=0.28)


# Connect to Redis
if __name__ == "__main__":
    worker = Worker([predict_queue], connection=redis_conn)
    worker.work()
