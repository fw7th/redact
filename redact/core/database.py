from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from redact.core.config import get_database_urls

ASYNC_DB_URL, SYNC_DB_URL = get_database_urls()

# Validate environment variable
if not ASYNC_DB_URL or SYNC_DB_URL:
    raise ValueError("Missing DB_URL or SYNC_DB_URL. Check .env or CI secrets.")

# Async engine for FastAPI
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine for RQ jobs
sync_engine = create_engine(SYNC_DB_URL, echo=True)
SessionLocal = sessionmaker(bind=sync_engine)


# Dependency to get DB session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    with SessionLocal() as session:
        yield session


def init_sync_db():
    SQLModel.metadata.create_all(sync_engine)


# Func to initialize_db
async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
