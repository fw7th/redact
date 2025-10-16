# tests/test_main.py
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_prediction_success(client, mock_session):
    """Test successful file upload and prediction creation"""

    fake_batch_id = uuid4()
    fake_job_id = "test-job-123"

    # Mock the dependencies
    with (
        patch(
            "api.main.create_batch_and_files", new_callable=AsyncMock
        ) as mock_create_batch,
        patch("api.main.predict_queue") as mock_queue,
        patch("api.main.get_async_session", return_value=mock_session),
        patch("builtins.open", create=True),
        patch("os.path.exists", return_value=False),
        patch("shutil.copyfileobj"),
    ):
        # Configure mocks
        mock_create_batch.return_value = fake_batch_id
        mock_job = MagicMock()
        mock_job.id = fake_job_id
        mock_queue.enqueue.return_value = mock_job
        mock_queue.job_ids = [fake_job_id]

        # Create fake file data
        fake_image = BytesIO(b"fake image content")
        files = [("files", ("test.jpg", fake_image, "image/jpeg"))]

        # Act: Make the request
        response = await client.post("/predict", files=files)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == fake_job_id
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_create_prediction_invalid_file_type(client):
    """Test rejection of invalid file types"""

    fake_file = BytesIO(b"fake content")
    files = [("files", ("test.pdf", fake_file, "application/pdf"))]

    response = await client.post("/predict", files=files)

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_prediction_file_too_large(client):
    """Test rejection of files that are too large"""

    huge_content = b"x" * (11 * 1024 * 1024)
    fake_file = BytesIO(huge_content)
    files = [("files", ("huge.jpg", fake_file, "image/jpeg"))]

    response = await client.post("/predict", files=files)

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_prediction_multiple_files(client):
    """Test uploading multiple valid files"""

    with (
        patch(
            "api.main.create_batch_and_files", new_callable=AsyncMock
        ) as mock_create_batch,
        patch("api.main.predict_queue") as mock_queue,
        patch("api.main.get_async_session"),
        patch("builtins.open", create=True),
        patch("os.path.exists", return_value=False),
        patch("shutil.copyfileobj"),
    ):
        mock_create_batch.return_value = uuid4()
        mock_job = MagicMock()
        mock_job.id = "test-job-123"
        mock_queue.enqueue.return_value = mock_job
        mock_queue.job_ids = ["test-job-123"]

        # Multiple files
        files = [
            ("files", ("test1.jpg", BytesIO(b"content1"), "image/jpeg")),
            ("files", ("test2.png", BytesIO(b"content2"), "image/png")),
        ]

        response = await client.post("/predict", files=files)

        assert response.status_code == 200
