from redis import Redis
from rq import Queue, Worker

from redact.core.redis import predict_queue, redis_conn

# Connect to Redis
if __name__ == "__main__":
    worker = Worker([predict_queue], connection=redis_conn)
    worker.work()
