# tests/conftest.py
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from redact.api.main import app

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    """Provides an async HTTP client for testing FastAPI endpoints"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_session():
    """Provides a mocked AsyncSession for database operations"""
    session = AsyncMock(spec=AsyncSession)

    # Mock the context manager behavior for session.begin()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_context)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = mock_context

    session.add = MagicMock()
    session.add_all = MagicMock()

    return session


@pytest.fixture
def sync_mock_session():
    """Provides a mocked AsyncSession for database operations"""
    session = MagicMock(spec=Session)

    # Mock the context manager behavior for regular 'with' statement
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=None)

    # Mock common session methods
    session.get = MagicMock()
    session.execute = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()

    return session
