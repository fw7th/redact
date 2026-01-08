import os
import shutil
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from redact.core.config import IMAGE_DIR, REDACT_DIR, UPLOAD_DIR
from redact.core.database import get_async_session, init_async_db
from redact.core.log import LOG
from redact.core.redis import predict_queue
from redact.core.zip import zip_files
from redact.services.storage import (
    create_batch_and_files,
    delete_batch_db,
    get_file_id_by_batch,
    update_batch_status_async,
)
from redact.sqlschema.tables import Batch, BatchStatus, Files


def create_dirs():
    try:
        # Ensure the base directory exists when the application starts
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        REDACT_DIR.mkdir(parents=True, exist_ok=True)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
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
    # Example: database connection, loading models, etc.
    # Shutdown events: Code here runs when the application shuts down
    print("ML model loaded.")
    yield
    LOG.info("Application shutdown: Cleaning up resources...")
    LOG.info("Cleanup complete.")
    # Example: closing database connections, releasing resources


create_dirs()
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
            file_path = os.path.join(UPLOAD_DIR, file.filename)

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
    await update_batch_status_async(batch_id, BatchStatus.uploaded)

    # Enqueue model processing job
    predict_queue.enqueue("redact.workers.inference.sync_full_inference", batch_id)

    return {
        "batch_id": batch_id,
        "status": "queued",
    }


@app.get("/predict/check/{batch_id}")
async def get_task_status(
    batch_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    """Check the status of a task"""
    try:
        status_query = await session.execute(
            select(Batch.status).where(Batch.id == batch_id)
        )
        status = status_query.scalars().one()

        if status == BatchStatus.completed:
            return {"status": "completed"}

        elif status == BatchStatus.failed:
            return {"status": "failed"}

        elif status == BatchStatus.processing:
            return {"status": "processing"}

        else:
            return {"status": "queued"}

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")


# For Users to request a file, maybe their download.
@app.get("/predict/{batch_id}")
async def get_image(batch_id: UUID, session: AsyncSession = Depends(get_async_session)):
    file_list = []
    try:
        file_ids = await get_file_id_by_batch(batch_id, session)
        for file_id in file_ids:
            str_uuid = str(file_id)

            result = await session.execute(
                select(Files.redact_filename).where(Files.file_id == str_uuid)
            )

            redact_image_name = result.scalars().one()
            file_path = os.path.join(REDACT_DIR, redact_image_name)
            if not os.path.exists(file_path):
                # Handle case where image is not found.
                raise HTTPException(status_code=404, detail="File not found.")

            file_list.append(file_path)
        # Optional: Add access control logic here
        # Check DB to see if the user should have access to this file
        zip_bytes = zip_files(file_list)
        zip_filename = "redacted_files.zip"

        return Response(
            content=zip_bytes.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
        )

    except:
        raise HTTPException(
            detail="There was an error processing the data", status_code=400
        )

    finally:
        zip_bytes.close()


@app.delete("/predict/drop/{batch_id}")
async def drop_batch(
    batch_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    try:
        await delete_batch_db(batch_id, session)

    except Exception:
        return {f"Batch ID: {batch_id} is not a valid ID."}

    return {f"Batch {batch_id} deleted from database."}
