import argparse
import os
import sys

sys.path.append("/home/fw7th/.pyenv/versions/mlenv/lib/python3.10/site-packages/")
from gliner import GLiNER


def main(args):
    # Load the GLiNER model
    gliner_model = GLiNER.from_pretrained(args.model_path)

    # Export to ONNX format
    gliner_model.export_to_onnx(
        save_dir=args.save_path,
        onnx_filename=args.file_name,
        quantized_filename=args.quantized_file_name,
        quantize=args.quantize,
        opset=args.opset,
    )

    print(f"Model exported successfully to {args.save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert GLiNER model to ONNX format")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path or HuggingFace model ID (e.g., urchade/gliner_small-v2.1)",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default="./onnx_models",
        help="Directory to save ONNX model",
    )
    parser.add_argument(
        "--file_name",
        type=str,
        default="model.onnx",
        help="Name of the ONNX model file",
    )
    parser.add_argument(
        "--quantized_file_name",
        type=str,
        default="model_quantized.onnx",
        help="Name of the quantized ONNX model file",
    )
    parser.add_argument(
        "--opset", type=int, default=19, help="ONNX opset version (default: 19)"
    )
    parser.add_argument(
        "--quantize", action="store_true", help="Also create a quantized INT8 version"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

    main(args)
    print("Done!")
