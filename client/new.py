import os
import time
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
    "/home/fw7th/Pictures/mobile2.jpg",
    "/home/fw7th/Pictures/test.jpg",
]  # These would be your file paths.

files_to_upload = []
for path in paths:
    files_to_upload.append(
        (
            "files",
            (os.path.basename(path), open(path, "rb"), "image/jpg"),
        )
    )


batch_id = "5aec6ee0-6681-4269-bce8-d99b1bf277a2"
counter = 1
while True:
    status = requests.get(f"http://localhost:8000/predict/check/{batch_id}")
    data = status.json()
    if data["status"] == "completed":
        try:
            # Use stream=True for efficient downloading of larger files
            response = requests.get(
                f"http://localhost:8000/predict/{batch_id}", stream=True
            )
            response.raise_for_status()

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
