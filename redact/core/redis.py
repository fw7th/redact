import os

from dotenv import load_dotenv
from redis import Redis
from rq import Queue

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Connect to Redis
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
predict_queue = Queue("high", connection=redis_conn)
