from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from redact.core.config import get_database_urls


def get_async_engine():
    ASYNC_DB_URL, _ = get_database_urls()
    return create_async_engine(ASYNC_DB_URL, echo=True)


def get_sync_engine():
    _, SYNC_DB_URL = get_database_urls()
    return create_engine(SYNC_DB_URL, echo=True)


async_engine = get_async_engine()
sync_engine = get_sync_engine()

# Async engine for FastAPI
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for RQ jobs
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
