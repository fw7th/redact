import asyncio
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import AsyncClient, acreate_client

from redact.core.database import init_async_db

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in environment variables")


_supabase_client: Optional[AsyncClient] = None
_lock = asyncio.Lock()


async def get_supabase_client() -> AsyncClient:
    """Get or create the Supabase client (works in any context)."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Use lock to prevent multiple initializations in concurrent contexts
    async with _lock:
        # Double-check after acquiring lock
        if _supabase_client is not None:
            return _supabase_client

        _supabase_client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
        # thread safe, lazy initialized, non-redundant.


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events: Code here runs when the application starts
    global _supabase_client
    print("Application startup: Initializing resources...")

    # Create the client
    _supabase_client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client created successfully.")

    await init_async_db()
    # Example: database connection, loading models, etc.
    # Shutdown events: Code here runs when the application shuts down
    print("ML model loaded.")
    yield
    print("Application shutdown: Cleaning up resources...")
    print("Cleanup complete.")
    # Example: closing database connections, releasing resources


app = FastAPI(lifespan=lifespan)
