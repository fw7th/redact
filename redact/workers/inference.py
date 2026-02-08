import asyncio
import json
import os
import sys
import time
from uuid import UUID

# sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/") local dev hack
import cv2
import numpy as np
import pytesseract
from sqlmodel import select

from redact.core.config import SUPABASE_BUCKET, get_supabase_client
from redact.core.database import AsyncSessionLocal
from redact.services.storage import get_file_id_by_batch, update_batch_status_async
from redact.sqlschema.tables import Files, FileStatus
from redact.workers.worker import predict_entities

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


async def NER(batch_id: UUID):
    """
    Perform NER with the loaded model.
    """
    async with AsyncSessionLocal() as session:
        file_ids = await get_file_id_by_batch(batch_id, session)
        for file_id in file_ids:
            str_uuid = str(file_id)

            try:
                result = await session.execute(
                    select(Files.json_data).where(Files.file_id == str_uuid)
                )

                data = result.scalars().one()

                # Join full text
                full_text = " ".join(result["text"] for result in data["ocr"])

                try:
                    entities = await asyncio.to_thread(
                        predict_entities, full_text, labels
                    )  # Perform NER w/ GLiNER

                    # Build fast lookup dict: word -> label
                    entity_map = {}
                    for entity in entities:
                        for token in entity["text"].split(" "):
                            entity_map[token] = entity["label"]

                    # Update OCR records using 0(1) lookup
                    for item in data["ocr"]:
                        txt = item["text"]
                        if txt in entity_map:
                            item["entity"] = entity_map[txt]

                    # Update the DB to store the JSON
                except Exception as e:
                    print(f"Error performing NER on images. {e}")

                json_table = await session.get(Files, str_uuid)
                if not json_table:
                    raise ValueError(f"Document {str_uuid} not found.")

                json_table.json_data = data
                session.add(json_table)
                await session.commit()
                await session.refresh(json_table)

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the file '{file_id}'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")


async def redact(batch_id):
    async with AsyncSessionLocal() as session:
        file_ids = await get_file_id_by_batch(batch_id, session)
        for file_id in file_ids:
            str_uuid = str(file_id)

            result = await session.execute(
                select(Files.filename, Files.json_data).where(Files.file_id == str_uuid)
            )
            row = result.first()
            image, data = row  # return (image_name, json) from query

            image_name, old_extension = os.path.splitext(
                image
            )  # Get image name w/o extension

            document_path = f"uploads/{image}"  # Path to uploaded images

            supabase_client = await get_supabase_client()
            supabase_buffer = await supabase_client.storage.from_(
                SUPABASE_BUCKET
            ).download(
                path=document_path,
            )

            nparr = np.frombuffer(supabase_buffer, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            copied_image = cv_image.copy()
            try:
                for item in data["ocr"]:
                    if item["entity"] is not None:
                        redact_area = [
                            [bbox_num // 3 for bbox_num in inner_list]
                            for inner_list in item["bbox"]
                        ]  # Scale image bbox back to original value
                        top_left = redact_area[0]
                        bottom_right = redact_area[1]
                        color = (0, 0, 0)  # Black color
                        thickness = -1  # Filled rectangle

                        cv2.rectangle(
                            copied_image, top_left, bottom_right, color, thickness
                        )
                    else:
                        pass

                redact_image_name = f"{image_name}_redacted{old_extension}"

                encode_param = [
                    int(cv2.IMWRITE_JPEG_QUALITY),
                    95,
                ]  # Set JPEG quality to 95
                success, encoded_buffer = cv2.imencode(
                    f"{old_extension}", copied_image, encode_param
                )  # Decode image back to jpeg

                if not success:
                    raise Exception("Could not encode image buffer")

                image_bytes = encoded_buffer.tobytes()

                try:
                    save_path = f"redacted/{redact_image_name}"

                    supabase_client = await get_supabase_client()
                    await supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                        path=save_path,
                        file=image_bytes,
                        file_options={
                            "content-type": "image/jpeg",
                            "upsert": "true",
                        },
                    )

                except Exception as e:
                    print(f"Redacted image could not be saved: {e}")

            except Exception as e:
                print(f"Could not resolve file name. Error: {e}")

            json_table = await session.get(Files, str_uuid)
            if not json_table:
                raise ValueError(f"Document {str_uuid} not found.")

            json_table.redact_filename = redact_image_name
            session.add(json_table)
            await session.commit()
            await session.refresh(json_table)


def preprocess_ocr(buffer):
    # Read image
    img = cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)

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

            document_path = f"uploads/{document}"

            supabase_client = await get_supabase_client()
            supabase_buffer = await supabase_client.storage.from_(
                SUPABASE_BUCKET
            ).download(
                document_path,
            )

            nparr = np.frombuffer(
                supabase_buffer, np.uint8
            )  # Conv supabase buffer to np array
            img = await asyncio.to_thread(preprocess_ocr, nparr)
            results = await asyncio.to_thread(
                pytesseract.image_to_data, img, output_type=pytesseract.Output.DICT
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

                # Filter out empty text
                if len(text.strip()) > 0:
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


async def full_inference(batch_id: UUID):
    """Performs OCR + NER"""
    print(f"Processing batch: {batch_id}")
    try:
        start_time = time.perf_counter()

        await update_batch_status_async(batch_id, FileStatus.processing)
        await document_ocr(batch_id)
        await NER(batch_id)
        await redact(batch_id)
        await update_batch_status_async(batch_id, FileStatus.complete)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        print(f"Task {batch_id} completed after {elapsed_time:.3f} seconds")

    except Exception as e:
        print(f"Exception: {e}")
        await update_batch_status_async(batch_id, FileStatus.failed)


def sync_full_inference(batch_id: UUID):
    asyncio.run(full_inference(batch_id))
