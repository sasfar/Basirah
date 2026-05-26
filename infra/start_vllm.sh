#!/bin/bash
# Start vLLM server for Basirah

MODEL_PATH="/home/syeddgx/Projects/Basirah/data/models/llm"
PORT=8000
GPU=0

export CUDA_VISIBLE_DEVICES=$GPU

echo "Starting vLLM server..."
echo "Model: $MODEL_PATH"
echo "Port: $PORT"
echo "GPU: $GPU"

/home/syeddgx/miniforge3/bin/python3 -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name basirah-llm \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --host 0.0.0.0 \
  --port $PORT
