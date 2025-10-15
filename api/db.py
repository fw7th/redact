import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate environment variable
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_async_engine(DATABASE_URL, echo=True)


# Dependency to get DB session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


# Func to initialize_db
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
