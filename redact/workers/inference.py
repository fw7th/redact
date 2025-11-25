import json
import os
import time
from uuid import UUID

import cv2
import pytesseract
from sqlalchemy.orm import Session

from redact.services.storage import update_batch_status
from redact.sqlschema.tables import FileStatus


class Inference:
    def __init__(self, model, batch_id: UUID, task_id: str, duration: int = 5):
        self.model = model
        self.labels = [
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

    def NER(self, json_files: list[str]):
        for json_path in json_files:
            try:
                with open(json_path, "r") as file:
                    data = json.load(file)

                texts = " ".join(result["text"] for result in data["ocr"])

                entities = self.model.predict_entities(
                    texts, self.labels, threshold=0.25
                )

                for i in range(0, len(data["ocr"]))
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

    def redact(self, json_files: list[str]):
        for json_path in json_files:
            try:
                with open(json_path, "r") as file:
                    data = json.load(file)

                    """"Stiill gottta finish""""

            except FileNotFoundError:
                print(f"Error: The file '{json_path}' was not found.")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from the file '{json_path}'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    def preprocess_ocr(self, image: str):
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

    def document_ocr(self, save_directory: str, documents: list):
        # Create the directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        for document in documents:
            data = {"ocr": []}

            file_with_extension = os.path.basename(document)
            file_name, old_extension = os.path.splitext(file_with_extension)
            file_plus_json_extension = f"{file_name}" + ".json"
            jsonpath = os.path.join(save_directory, file_plus_json_extension)

            # Open an image
            img = self.preprocess_ocr(document)
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

            with open(jsonpath, "w") as f:
                json.dump(data, f, indent=4)

            print(f"Data from {file_with_extension} saved to {jsonpath}")

    def full_inference(self):
        """Performs OCR + NER"""
        print(f"Starting task {self.task_id}")
        try:
            update_batch_status(self.batch_id, FileStatus.processing)
            time.sleep(self.duration)
            update_batch_status(self.batch_id, FileStatus.complete)

        except Exception as e:
            print(f"Exception: {e}")
            update_batch_status(self.batch_id, FileStatus.failed)

        result = f"Task {self.task_id} completed after {self.duration} seconds"
        print(result)
        return result
