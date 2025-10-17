from redis import Redis
from rq import Queue

from redact.core.config import get_redis_dirs

REDIS_HOST, REDIS_PORT = get_redis_dirs()

# Connect to Redis
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
predict_queue = Queue("high", connection=redis_conn)
