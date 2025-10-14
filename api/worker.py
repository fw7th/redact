from redis import Redis
from rq import Queue, Worker

# Connect to Redis
redis_conn = Redis(host="localhost", port=6379, db=0)

if __name__ == "__main__":
    queue = Queue("high", connection=redis_conn)  # priority queue

    worker = Worker([queue], connection=redis_conn)
    worker.work()
