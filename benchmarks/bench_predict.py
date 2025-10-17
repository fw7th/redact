import time
from pathlib import Path

import httpx

# from core.log import LOG

URL = "http://localhost:8000/predict"
TEST_IMAGE = Path(__file__).parent / "test_assets" / "file3.webp"


def benchmark_predict():
    files = [("files", ("file3.webp", open(TEST_IMAGE, "rb"), "image/webp"))]
    start = time.time()

    response = httpx.post(URL, files=files)
    duration = time.time() - start

    print(f"Status: {response.status_code}")
    print(f"Time: {duration:.2f}s")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    benchmark_predict()
