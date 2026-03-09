# ASR Triton Service

> [中文說明 (Chinese README)](README_zh.md)

This project provides a standalone Triton Inference Server setup for ASR (Automatic Speech Recognition) using `faster-whisper`.

## Directory Structure

```
asr-triton-service/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local deployment configuration
├── models/                 # Model repository
├── scripts/                # Helper scripts
│   ├── run_server.sh       # Build, add model, and start server
│   └── test_inference.py   # Test inference client
└── templates/              # Model templates
    └── whisper_template/   # Template for adding new models
```

## Getting Started

### 1. Start the Server

```bash
# Start the server (models must already exist)
./scripts/run_server.sh

# Build the Docker image and start the server
./scripts/run_server.sh --build
```

### 2. Add a New Model

`<model_name>` is the name of the model on the Triton server, `<hf_repo_id>` is the HuggingFace repo ID.

```bash
./scripts/run_server.sh --model <model_name> --repo_id <hf_repo_id>

# Example (first time, with --build):
./scripts/run_server.sh --model asia-new-bay-l-v2-ct --repo_id jeff7522553/asia-new-bay-l-v2-ct --build
```

This script will automatically:
1. Create the model directory from the template
2. Download model weights from HuggingFace
3. Start the server (add `--build` to rebuild the Docker image)

If the model already exists, steps 1 and 2 will be skipped.

### 3. Custom Ports

```bash
# Custom HTTP port
./scripts/run_server.sh --port 9000

# Custom all ports
./scripts/run_server.sh --port 9000 --grpc-port 9001 --metrics-port 9002
```

Default ports: HTTP `8000`, gRPC `8001`, Metrics `8002`.

### 4. Restart Server (manual)

```bash
docker compose restart
```

### 5. Test Inference

```bash
# Install dependencies
pip install -r requirements.txt

# Run test (generates dummy audio if file not provided)
python3 scripts/test_inference.py --model <model_name> --audio <audio_path>

# Examples:
# Specifying language is recommended for better accuracy
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio zh-test.wav --lang zh
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio en-test.wav --lang en

# Specify a different server URL
python3 scripts/test_inference.py --url 192.168.1.100:8000 --model asia-new-bay-l-v2-ct --audio zh-test.wav
```

## Customization

-   **Dependencies**: Python packages are defined in `Dockerfile` under the `pip install` section.
-   **Model Logic**: The inference logic is in `models/<model_name>/1/model.py`. You can modify the `TritonPythonModel` class to change how audio is processed or how the model is called.
