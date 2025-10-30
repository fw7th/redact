import os
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from rq.job import Job
from sqlmodel.ext.asyncio.session import AsyncSession

from redact.core.config import BASE_DIR
from redact.core.database import get_async_session, init_async_db, init_sync_db
from redact.core.log import LOG
from redact.core.redis import predict_queue, redis_conn
from redact.services.storage import create_batch_and_files
from redact.workers.inference import simulate_model_work

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)  # goes from api/main.py → project/
FULL_DIR = PROJECT_ROOT / BASE_DIR


def create_base():
    try:
        # Ensure the base directory exists when the application starts
        FULL_DIR.mkdir(parents=True, exist_ok=True)
        return {"message": "Base directory created successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create directory: {str(e)}"
        )


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events: Code here runs when the application starts
    LOG.info("Application startup: Initializing resources...")
    await init_async_db()
    init_sync_db()
    # Example: database connection, loading models, etc.
    yield
    # Shutdown events: Code here runs when the application shuts down
    LOG.info("Application shutdown: Cleaning up resources...")
    # Example: closing database connections, releasing resources


create_base()
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def favicon():
    return Response(status_code=204)  # No Content


@app.post("/predict")
async def create_prediction(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    uploaded_files = []
    for file in files:
        uploaded_files.append(file.filename)
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,  # Bad Request
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            )

        # Validate file size (e.g., max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise HTTPException(
                status_code=413,  # Payload Too Large
                detail=f"File too large. Maximum size: {max_size / (1024 * 1024)}MB",
            )

        # Validate filename
        if not file.filename or file.filename.strip() == "":
            raise HTTPException(
                status_code=400,  # Bad Request
                detail="Filename cannot be empty",
            )

        try:
            # Save file to disk
            file_path = os.path.join(FULL_DIR, file.filename)

            """
            # Check if file already exists
            if os.path.exists(file_path):
                raise HTTPException(
                    status_code=409,  # Conflict
                    detail=f"File '{file.filename}' already exists",
                )
            """

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except PermissionError:
            raise HTTPException(
                status_code=403,  # Forbidden
                detail="Permission denied when writing file",
            )
        except OSError as e:
            raise HTTPException(
                status_code=500,  # Internal Server Error
                detail=f"Failed to save file: {str(e)}",
            )
        except Exception as e:
            # Cleanup: remove file if it was partially written
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,  # Internal Server Error
                detail=f"Unexpected error during file upload: {str(e)}",
            )

        finally:
            await file.close()

    # Save to database
    batch_id = await create_batch_and_files(files, session)

    # Simulate work (model call)
    job = predict_queue.enqueue(
        simulate_model_work,
        batch_id,
        f"task_{int(time.time())}",
        30,
        job_id="0",
    )

    queued_job_ids = predict_queue.job_ids
    LOG.info(f"Queued Job IDs: {queued_job_ids}")

    return {
        "job_id": job.id,
        "status": "queued",
    }


@app.get("/predict/{job_id}")
async def get_task_status(job_id: str):
    """Check the status of a task"""
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None,
        }
    except Exception as e:
        return {"error": f"Job {job_id} not found"}


"""
For Users to request a file, maybe their download etc.
@app.get("/files/{filename}")
async def get_file(filename: str, user: User = Depends(get_current_user)):
    file_path = f"uploads/{user.id}/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    # Optional: Add access control logic here
    # Check DB to see if the user should have access to this file

    return FileResponse(
        path=file_path, media_type="application/octet-stream", filename=filename
    )
"""
