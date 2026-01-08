import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()
ASYNC_DB_URL = os.getenv("ASYNC_DB_URL")

# Validate environment variable
if not ASYNC_DB_URL:
    raise ValueError("ASYNC_DB_URL environment variable is not set.")

# Async engine for FastAPI
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency to get DB session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Func to initialize_db
async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
