import json
import os
import sys

import numpy as np

sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")

import cv2
from gliner import GLiNER

model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

labels = [
    "person",
    "organization",
    "phone number",
    "mobile phone number",
    "landline phone number",
    "email",
    "email address",
    "address",
    "passport number",
    "identity card number",
    "national id number",
    "bank account number",
    "account number",
    "iban",
    "credit card number",
    "cvv",
    "credit card expiration date",
    "social security number",
    "date of birth",
    "date",
]


def NER(json_files: list[str]):
    for json_path in json_files:
        with open(json_path, "r") as file:
            data = json.load(file)

        # Gather full text for NER model
        full_text = " ".join(result["text"] for result in data["ocr"])

        entities = model.predict_entities(full_text, labels, threshold=0.28)

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

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)


def redact(json_files: list[str], images: list[str]):
    for json_file, image in zip(json_files, images):
        with open(json_file, "r") as file:
            data = json.load(file)

        image_with_extension = os.path.basename(image)
        json_with_extension = os.path.basename(json_file)

        image_name, old_extension = os.path.splitext(image_with_extension)
        json_name, old_extension_ = os.path.splitext(json_with_extension)

        cv_image = cv2.imread(image)
        copied_image = cv_image.copy()
        try:
            if image_name == json_name:
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

            cv2.imwrite(
                f"../Pictures/{image_name}_redacted.{old_extension}", copied_image
            )

        except Exception as e:
            print(f"Could not resolve file name. Error: {e}")


NER(["./extracts/test.json", "./extracts/mobile2.json"])
redact(
    ["./extracts/test.json", "./extracts/mobile2.json"],
    ["../Pictures/test.jpg", "../Pictures/mobile2.jpg"],
)
