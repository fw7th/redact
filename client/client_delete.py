"""
# client_delete.py -> Provides functionality to completely clean your files from the server.
Deletes your files from the database, reads from the auto-generated 'Your_Files' directory.
Keep in mind you need the batch's processed ID to drop files from the supabase bucket and database.

# For local development, replace `url` with your local server URL.
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

url = f"https://redact7th.vercel.app/drop/{batch_id}"

# Send the DELETE request
response = requests.delete(url)

# Check the response status code
if response.status_code == 200:
    print(response.json())
elif response.status_code == 404:
    print("Resource not found.")
else:
    print(f"Failed to delete resource. Status code: {response.status_code}")
