#!/bin/bash
# Start llama.cpp server for Basirah with OpenAI-compatible API

MODEL_PATH="/home/syeddgx/Projects/Basirah/data/models/llm-gguf/Qwen2.5-7B-Instruct-Q5_K_M.gguf"
PORT=8000
GPU_LAYERS=99  # Offload all layers to GPU

export CUDA_VISIBLE_DEVICES=0

echo "Starting llama.cpp server..."
echo "Model: $MODEL_PATH"
echo "Port: $PORT"
echo "GPU Layers: $GPU_LAYERS"

/home/syeddgx/miniforge3/bin/python3 -m llama_cpp.server \
  --model "$MODEL_PATH" \
  --host 0.0.0.0 \
  --port $PORT \
  --n_gpu_layers $GPU_LAYERS \
  --n_ctx 8192 \
  --chat_format chatml \
  --verbose False
