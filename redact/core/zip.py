import asyncio
import io
import os
import zipfile

from redact.core.config import SUPABASE_BUCKET

CHUNK_SIZE = 1024


async def zip_files(supabase_client, file_list: list):
    # Create a BytesIO object to write the zip file into memory
    s = io.BytesIO()
    with zipfile.ZipFile(s, "w") as zf:
        for file_path in file_list:
            # Stream the file from supabase bucket
            image_data = await supabase_client.storage.from_(SUPABASE_BUCKET).download(
                path=file_path,
            )
            # Add file to the zip archive, using just the filename
            minSize = (30, 30)
            zf.writestr(os.path.basename(file_path), image_data)

    # After writing, seek back to the beginning of the BytesIO object
    s.seek(0)
    return s


async def stream_buffer(buffer: io.BytesIO):
    """Async generator to stream buffer contents in chunks."""
    # Seek to the beginning of the BytesIO object to ensure reading from the start
    # buffer.seek(0)

    while True:
        # Read a chunk of data from the BytesIO object
        chunk = buffer.read(CHUNK_SIZE)

        # If no more data is read (end of stream), break the loop
        if not chunk:
            break

        # Yield the chunk of bytes asynchronously
        yield chunk

        # Optionally, introduce a small await to allow the event loop to breathe
        # if the processing is very fast and you want to ensure fairness.
        # This is often not necessary for in-memory BytesIO but useful for real async I/O.
        await asyncio.sleep(0)
