# tests/test_storage.py
import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException, UploadFile

from redact.services.storage import create_batch_and_files
from redact.sqlschema.tables import Batch, Files


@pytest.mark.asyncio
async def test_create_batch_and_files_success(mock_session):
    """Test successful batch and file creation"""
    # Arrange: Create fake uploaded files
    fake_file1 = MagicMock(spec=UploadFile)
    fake_file1.filename = "test1.jpg"

    fake_file2 = MagicMock(spec=UploadFile)
    fake_file2.filename = "test2.png"

    files = [fake_file1, fake_file2]

    # Act: Call the function
    batch_id = await create_batch_and_files(files, mock_session)

    # Assert: Check the results
    assert isinstance(batch_id, UUID)
    mock_session.add.assert_called_once()
    mock_session.add_all.assert_called_once()

    # Check that 2 file objects were created
    call_args = mock_session.add_all.call_args
    file_objs = call_args[0][0]
    assert len(file_objs) == 2
    assert file_objs[0].filename == "test1.jpg"
    assert file_objs[1].filename == "test2.png"


@pytest.mark.asyncio
async def test_create_batch_and_files_db_error(mock_session):
    """Test database error handling"""
    from sqlalchemy.exc import SQLAlchemyError

    # Arrange: Make session.begin() raise an error
    mock_session.begin.side_effect = SQLAlchemyError("Connection failed")

    fake_file = MagicMock(spec=UploadFile)
    fake_file.filename = "test.jpg"

    # Act & Assert: Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await create_batch_and_files([fake_file], mock_session)

    assert exc_info.value.status_code == 500
    assert "Failed to store batch" in exc_info.value.detail


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" ""
"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" ""
