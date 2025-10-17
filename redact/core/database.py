# redact/core/database.py
from typing import AsyncGenerator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from redact.core.config import get_database_urls

async_engine: Optional[AsyncEngine] = None
sync_engine: Optional[Engine] = None
AsyncSessionLocal: Optional[sessionmaker] = None
SessionLocal: Optional[sessionmaker] = None


def init_engines():
    global async_engine, sync_engine, AsyncSessionLocal, SessionLocal

    ASYNC_DB_URL, SYNC_DB_URL = get_database_urls()

    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    sync_engine = create_engine(SYNC_DB_URL, echo=True)

    AsyncSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    SessionLocal = sessionmaker(bind=sync_engine)


# Dependency
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    if not AsyncSessionLocal:
        raise RuntimeError("Async engine not initialized")
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    if not SessionLocal:
        raise RuntimeError("Sync engine not initialized")
    with SessionLocal() as session:
        yield session


def init_sync_db():
    if not sync_engine:
        raise RuntimeError("Sync engine not initialized")
    SQLModel.metadata.create_all(sync_engine)


async def init_async_db():
    if not async_engine:
        raise RuntimeError("Async engine not initialized")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
