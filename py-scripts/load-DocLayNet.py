import os

from datasets import load_dataset


def download_doclaynet():
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")

    local_dir = os.path.join(current_dir, "data", "doclaynet_small")

    try:
        os.mkdir(local_dir)
        print(f"Directory '{local_dir}' created successfully.")
    except FileExistsError:
        print(f"Directory '{local_dir}' already exists.")
        pass

    dataset = load_dataset(
        "pierreguillou/DocLayNet-small", revision="refs/convert/parquet"
    )
    print(f"Dataset loaded successfully: {dataset}")

    print(f"Saving dataset to disk at {local_dir}...")
    dataset.save_to_disk(local_dir)
    print(f"Dataset successfully saved to the directory: {local_dir}")


if __name__ == "__main__":
    download_doclaynet()
