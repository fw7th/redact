import subprocess
import sys
import time
import warnings
from multiprocessing import Process

sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")
warnings.filterwarnings(
    "ignore",
    message="The sentencepiece tokenizer that you are converting to a fast tokenizer uses the byte fallback option",
)
print("Starting test...")

full_text = """Okosa David, Gojo Satoru, Bill Gates, okosa7th@gmail.com"""
labels = ["Person", "Date", "Email"]


def run_inference():
    """This runs in a subprocess"""
    print("Subprocess started")
    try:
        gliner_start = time.time()
        from gliner import GLiNER

        gliner_time = time.time() - gliner_start
        print(f"GLiNER import took: {gliner_time:.2f}s")

        model_start = time.time()
        ML_MODEL = GLiNER.from_pretrained(
            "/home/fw7th/redact/data/gliner_urchade/",
            local_files_only=True,
        )
        model_time = time.time() - model_start
        print(f"Model loading in main process took: {model_time:.2f}s")

        start = time.time()
        print("About to call predict_entities...")
        entities = ML_MODEL.predict_entities(full_text, labels)
        print("predict_entities returned")
        for entity in entities:
            print(entity["text"], "=>", entity["label"])
        elapsed = time.time() - start
        print(f"Subprocess inference took: {elapsed:.2f}s")

    except Exception as e:
        print(f"Error in subprocess: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("Testing inference in subprocess...")
    p = Process(target=run_inference)
    p.start()
    p.join(timeout=90)

    if p.is_alive():
        print("HUNG: Process is still alive after 90 seconds")
        p.terminate()
        p.join()
    else:
        print(f"Process exited with code: {p.exitcode}")
