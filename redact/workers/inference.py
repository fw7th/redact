import asyncio
import json
import os
import sys
import time
from uuid import UUID

# Temporary, just for prod
sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")

import cv2
import pytesseract
from sqlalchemy.orm import Session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from redact.core.config import REDACT_DIR, UPLOAD_DIR
from redact.core.database import AsyncSessionLocal, get_async_session
from redact.services.storage import get_file_id_by_batch, update_batch_status
from redact.sqlschema.tables import Batch, Files, FileStatus

labels = [
    "person",
    "credit card number",
    "email",
    "phone number",
    "gender",
    "marital status",
    "date",
    "social security number, health insurance",
    "location",
]


def NER(json_files: list[str], model):
    for json_path in json_files:
        try:
            with open(json_path, "r") as file:
                data = json.load(file)

            texts = " ".join(result["text"] for result in data["ocr"])

            entities = model.predict_entities(texts, labels, threshold=0.25)

            for i in range(0, len(data["ocr"])):
                for entity in entities:
                    if entity["text"] == data["ocr"][i]["text"]:
                        data["ocr"][i]["label"] = entity["label"]

                    print(entity["text"], "=>", entity["label"])

        except FileNotFoundError:
            print(f"Error: The file '{json_path}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{json_path}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def redact(json_files: list[str]):
    for json_path in json_files:
        try:
            with open(json_path, "r") as file:
                data = json.load(file)

        except FileNotFoundError:
            print(f"Error: The file '{json_path}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{json_path}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def preprocess_ocr(image: str):
    # Read image
    img = cv2.imread(image)

    # 1. Optional: scale image (helps Tesseract)
    sized = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale
    gray = cv2.cvtColor(sized, cv2.COLOR_BGR2GRAY)

    # 3. Noise reduction (Gaussian blur)
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. Adaptive threshold (handles uneven lighting)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 7
    )

    return thresh


def sync_document_ocr(batch_id: UUID):
    asyncio.run(document_ocr(batch_id))


async def document_ocr(batch_id: UUID):
    async with AsyncSessionLocal() as session:
        file_ids = await get_file_id_by_batch(batch_id, session)
        for file_id in file_ids:
            str_uuid = str(file_id)

            result = await session.execute(
                select(Files.filename).where(Files.file_id == str_uuid)
            )
            document = str(result.scalars().one())

            data = {"ocr": []}
            file_name, old_extension = os.path.splitext(document)
            document_path = os.path.join(UPLOAD_DIR, document)

            img = preprocess_ocr(document_path)
            results = pytesseract.image_to_data(
                img, output_type=pytesseract.Output.DICT
            )

            # Loop over each detected text localization
            for i in range(0, len(results["text"])):
                # Extract the bounding box coordinates, text, and confidence
                x = results["left"][i]
                y = results["top"][i]
                w = results["width"][i]
                h = results["height"][i]
                text = results["text"][i]
                conf = round(results["conf"][i], 3)

                # Filter out weak detections (e.g., confidence < 60) and empty text
                if len(text.strip()) > 0:
                    # print(f"Text: {text}, Bounding Box: ({x}, {y}, {w}, {h}), Confidence: {conf}%")
                    # You can also draw the bounding boxes on the image using Pillow
                    ocr_data = {
                        "text": text,
                        "bbox": [(x, y), (x + w, y + h)],
                        "entity": None,
                        "ocr_confidence": conf,
                    }

                    data["ocr"].append(ocr_data)

            json_table = await session.get(Files, str_uuid)
            if not json_table:
                raise ValueError(f"Document {str_uuid} not found.")

            json_table.json_data = data
            session.add(json_table)
            await session.commit()
            await session.refresh(json_table)


def full_inference(task_id):
    """Performs OCR + NER"""
    print(f"Starting task {task_id}")
    try:
        update_batch_status(batch_id, FileStatus.processing)
        time.sleep(duration)
        update_batch_status(batch_id, FileStatus.complete)

    except Exception as e:
        print(f"Exception: {e}")
        update_batch_status(batch_id, FileStatus.failed)

    result = f"Task {task_id} completed after {duration} seconds"
    print(result)
    return result


def simulate_model_work(batch_id: UUID, to_wait: int):
    print("Starting Inference")
    time.sleep(to_wait)
    print("Ending Inference")
