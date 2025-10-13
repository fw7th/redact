import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.staticfiles import StaticFiles

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


@app.post("/uploadfile/")
async def upload_image(file: UploadFile = File(...)):
    try:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception:
        raise HTTPException(status_code=500, detail="Could not upload file")
    finally:
        await file.close()  # Ensure the file is closed

    return {"filename": file.filename, "content_type": file.content_type}
