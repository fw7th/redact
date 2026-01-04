python convert_to_onnx.py \
    --model_path ./data/gliner_urchade \
    --save_path ./data/onnx_models \
    --file_name gliner_urchade_mid.onnx \
		--quantized_file_name gliner_mid_quant.onnx \
    --opset 19 \
		--quantize