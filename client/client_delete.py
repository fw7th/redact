"""
Deletes your files from the database, reads from the auto-generated 'Your_Files' directory.
"""

from pathlib import Path

import requests

script_dir = Path(
    __file__
).parent.parent  # Get the directory where the current script is located

filename = "batch_id.txt"
batch_id_file = script_dir / "Your_Files" / "batch_id.txt"


# Reads batch_id from the auto-generated file.
try:
    with batch_id_file.open("r") as f:
        batch_id = f.read()

except FileNotFoundError:
    print(f"Error: The file '{batch_id_file}' was not found at {batch_id_file}.")
except Exception as e:
    print(f"An error occurred: {e}")

url = f"http://localhost:8000/predict/drop/{batch_id}"

# Send the DELETE request
response = requests.delete(url)

# Check the response status code
if response.status_code == 200:
    print(response.json())
elif response.status_code == 404:
    print("Resource not found.")
else:
    print(f"Failed to delete resource. Status code: {response.status_code}")
