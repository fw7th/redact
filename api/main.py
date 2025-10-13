import datetime
import os
import shutil
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

import crud
from db import get_session, init_db
from models import jobs

BASE_DIR = "uploads"


def create_base():
    try:
        # Ensure the base directory exists when the application starts
        os.makedirs(BASE_DIR, exist_ok=True)
        return {"message": "Base directory created successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create directory: {str(e)}"
        )


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events: Code here runs when the application starts
    print("Application startup: Initializing resources...")
    create_base()
    init_db()
    # Example: database connection, loading models, etc.
    yield
    # Shutdown events: Code here runs when the application shuts down
    print("Application shutdown: Cleaning up resources...")
    # Example: closing database connections, releasing resources


app = FastAPI(lifespan=lifespan)
app.mount("/images", StaticFiles(directory="uploads"), name="images")


@app.get("/")
def favicon():
    return Response(status_code=204)  # No Content


@app.post("/uploadfile")
async def upload_image(
    file: UploadFile = File(...), session: Session = Depends(get_session)
):
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
        file_path = os.path.join(BASE_DIR, file.filename)

        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=409,  # Conflict
                detail=f"File '{file.filename}' already exists",
            )

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

    try:
        # Save to database
        image = crud.create_image(session, file.filename)
        session.add(image)
        session.commit()
        session.refresh(image)

    except Exception as e:
        # Cleanup: remove uploaded file if database operation fails
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        raise HTTPException(
            status_code=500,  # Internal Server Error
            detail=f"Failed to save to database: {str(e)}",
        )

    finally:
        await file.close()

    return {
        "image_id": image.id,
        "filename": image.filename,
        "status": image.status,
        "created_at": image.created_at,
    }


# Get image status by ID
@app.get("/images/{image_id}")
def get_image_status(image_id: int, session: Session = Depends(get_session)):
    return crud.get_image(session, image_id)


# Update status
@app.patch("/images/{image_id}/status")
def update_image_status(
    image_id: int, status: str, session: Session = Depends(get_session)
):
    return crud.update_image_status(session, image_id, status)
