import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Annotated, List
from uuid import UUID

import modal
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from supabase import AsyncClient

from redact.core.config import (
    MODAL_APP,
    SUPABASE_BUCKET,
    app,
    get_supabase_client,
)
from redact.core.database import get_async_session
from redact.services.storage import (
    create_batch_and_files,
    delete_batch_db,
    get_file_id_by_batch,
    update_batch_status_async,
)
from redact.sqlschema.tables import Batch, BatchStatus, Files

"""
# FOR LOCAL USE, UNCOMMENT THIS TO USE RQ INSTEAD OF MODAL.
from redact.core.redis import predict_queue
"""


@app.get("/")
async def root():
    return {
        "message": "Hey Hey! From 7th. You need to post an image here, it's just a backend for now."
    }


# Redirect /favicon.ico to the custom logo in assets
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/assets/favicon.ico", status_code=307)


@app.post("/predict")
async def create_prediction(
    supabase_client: Annotated[AsyncClient, Depends(get_supabase_client)],
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    for file in files:
        file_content = await file.read()

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

        # Save file to supabase storage bucket
        file_path = f"uploads/{file.filename}"

        try:
            # Use the storage client from the initialized supabase client
            await supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type, "upsert": "true"},
            )

            """ 
            # Check if file already exists
            if os.path.exists(file_path):
                raise HTTPException(
                    status_code=409,  # Conflict
                    detail=f"File '{file.filename}' already exists",
                )
            """

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
    remote_inference = modal.Function.from_name(MODAL_APP, "inference_work")
    result = remote_inference.spawn(batch_id)

    """
    # FOR LOCAL USE, UNCOMMENT THIS TO USE RQ INSTEAD OF MODAL.
    predict_queue.enqueue("redact.workers.inference.sync_full_inference", batch_id)
    """
    return {
        "batch_id": batch_id,
        "status": "queued",
    }


@app.get("/check/{batch_id}")
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


# For Users to request a file.
@app.get("/download/{batch_id}")
async def get_image(
    supabase_client: Annotated[AsyncClient, Depends(get_supabase_client)],
    batch_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        # Get file list for the batch
        file_list: List[str] = []
        file_ids = await get_file_id_by_batch(batch_id, session)
        for file_id in file_ids:
            str_uuid = str(file_id)
            result = await session.execute(
                select(Files.redact_filename).where(Files.file_id == str_uuid)
            )
            redact_image_name = result.scalars().one()
            file_path = f"redacted/{redact_image_name}"
            file_list.append(file_path)

        CHUNK_SIZE = 1024 * 1024  # 1 MB

        # Async generator that streams a zip
        async def zip_generator():
            with io.BytesIO() as mem_zip:
                with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file_path in file_list:
                        # Stream file from Supabase
                        data = await supabase_client.storage.from_(
                            SUPABASE_BUCKET
                        ).download(path=file_path)
                        zf.writestr(os.path.basename(file_path), data)

                mem_zip.seek(0)
                while chunk := mem_zip.read(CHUNK_SIZE):
                    yield chunk

        zip_filename = "redacted_files.zip"
        return StreamingResponse(
            zip_generator(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            detail="There was an error processing the data", status_code=400
        )


@app.delete("/drop/{batch_id}")
async def drop_batch(
    batch_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    try:
        await delete_batch_db(batch_id, session)

    except Exception:
        return {f"Batch ID: {batch_id} is not a valid ID."}

    return {f"Batch {batch_id} deleted from database."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
