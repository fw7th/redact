"""
# client_post.py
Provides Client side functionality. Allows you to upload files for processing.
Redacted documents are saved in a dir named "Your_Files", along with your batch_id.

Replace the variable `paths` with a list of your own local file paths.

For local development, replace `response` & `status` with appropriate local server URLs.
"""

import io
import os
import time
import zipfile
from pathlib import Path

import requests

CHUNK_SIZE = 4096
script_dir = Path(
    __file__
).parent.parent  # Get the directory where the current script is located

# Define the path for the new directory (relative to the current working directory)
directory_path = Path(script_dir / "Your_Files")

try:
    # Create the directory
    directory_path.mkdir()
    print(f"Directory '{directory_path}' created successfully.")
except FileExistsError:
    print(f"Directory '{directory_path}' already exists.")
except Exception as e:
    print(f"An error occurred: {e}")


local_filename = (
    directory_path / "redacted_files.zip"
)  # Redacted images are saved in a zip file

batch_id_file = directory_path / "batch_id.txt"

paths = [
    "/your/local/file/path1.jpg",
    "/your/local/file/path2.jpg",
]  # These would be your file paths.

files_to_upload = []
for path in paths:
    files_to_upload.append(
        (
            "files",
            (os.path.basename(path), open(path, "rb"), "image/jpg"),
        )
    )

# Start job
try:
    # Upload list of files to server
    response = requests.post(
        "https://redact7th.vercel.app/predict", files=files_to_upload
    )
    data = response.json()
    print(f"Data: {data}")
    batch_id = data["batch_id"]

    # Print the response from the server
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

finally:
    # Close all opened file handles after the request is complete
    for _, file_tuple in files_to_upload:
        file_tuple[1].close()

print(f"Batch ID: {batch_id}. Saved to batch_id.txt")
# Poll manually
counter = 1
while True:
    status = requests.get(f"https://redact7th.vercel.app/check/{batch_id}")
    data = status.json()
    if data["status"] == "completed":
        try:
            # Use stream=True for efficient downloading of larger files
            now = time.time()
            response = requests.get(
                f"https://redact7th.vercel.app/download/{batch_id}", stream=True
            )
            response.raise_for_status()
            later = time.time()
            print(f"Download took: {later - now}")

            # Save batch_id to delete files if you want to later.
            with open(batch_id_file, "w") as f:
                f.write(batch_id)

            # Open the local file in binary write mode ('wb')
            with open(local_filename, "wb") as outfile:
                # Use getbuffer() or getvalue() to get the bytes-like object
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    outfile.write(chunk)

            print(f"Download complete. File saved to {local_filename}")

            break

        except Exception as e:
            print(f"Failed to download the file: {e}")
            break

    elif data["status"] == "failed":
        print("Processing Failed.")
        break

    time.sleep(5)
    counter += 1
    print(f"Processing has taken {5 * counter} seconds.")
