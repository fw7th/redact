import os

from dotenv import load_dotenv

# Load .env in dev (skip if CI is already handling secrets)
if not os.getenv("CI"):
    load_dotenv()


def get_database_urls():
    async_url = os.getenv("DB_URL")
    sync_url = os.getenv("SYNC_DB_URL")

    if not async_url or not sync_url:
        raise ValueError("Missing DB_URL or SYNC_DB_URL. Check .env or CI secrets.")

    return async_url, sync_url


def get_base_dir():
    base_dir = os.getenv("BASE_DIR")

    if not base_dir:
        raise ValueError("Missing BASE_DIR. Check .env or CI secrets.")

    return base_dir


def get_redis_dirs():
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")

    if not redis_host or redis_port:
        raise ValueError("Missing REDIS_HOST or REDIS_PORT. Check .env or CI secrets.")

    return redis_host, redis_port
