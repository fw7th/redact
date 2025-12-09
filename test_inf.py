# test_subprocess.py
import subprocess
import sys
import time
from multiprocessing import Process

# Your full text from the OCR
full_text = """David Okosa, Gojou Satoru, what's the difference? 2025-11-24"""
labels = ["PERSON", "DATE", "EMAIL"]  # whatever labels you use


def run_inference():
    """This runs in a subprocess"""
    from redact.workers.worker import predict_entities

    start = time.time()
    result = predict_entities(full_text, labels)
    elapsed = time.time() - start
    print(f"Subprocess inference took: {elapsed:.2f}s")
    print(f"Result: {result}")


if __name__ == "__main__":
    print("Testing inference in subprocess...")

    # Method 1: Using multiprocessing.Process
    p = Process(target=run_inference)
    p.start()
    p.join(timeout=60)  # 30 second timeout

    if p.is_alive():
        print("HUNG: Process is still alive after 60 seconds")
        p.terminate()
    else:
        print(f"Process exited with code: {p.exitcode}")
