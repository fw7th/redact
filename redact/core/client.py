import glob
import io
import os
import time
import zipfile

import requests

CHUNK_SIZE = 1024

local_filename = "redacted_files.zip"
paths = ["/home/fw7th/Pictures/mobile2.jpg", "/home/fw7th/Pictures/test.jpg"]
files_to_upload = []

for path in paths:
    files_to_upload.append(
        ("files", (os.path.basename(path), open(path, "rb"), "image/jpg"))
    )
    # The format required is a list of tuples: ('form_field_name', ('filename', file_object, 'content_type'))
    # Use 'open(path, 'rb')' to open the file in binary read mode
    # The 'files' key on the server side (e.g., in FastAPI/Flask) must match the 'form_field_name'.

# Start job
try:
    # Upload list of files to server
    response = requests.post("http://localhost:8000/predict", files=files_to_upload)
    data = response.json()
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

print(batch_id)
# Poll manually
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

            print("About to save file")
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

    print(counter)
    time.sleep(5)
    counter += 1
