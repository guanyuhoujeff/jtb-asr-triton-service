# ASR Triton Service

> [中文說明 (Chinese README)](README_zh.md)

This project provides a standalone Triton Inference Server setup for ASR (Automatic Speech Recognition) using `faster-whisper`.

## Directory Structure

```
asr-triton-service/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local deployment configuration
├── models/                 # Model repository
└── scripts/                # Helper scripts
└── templates/              # Model templates
    └── whisper_template/   # Template for adding new models
```

## Getting Started

### 1. Build and Run

```bash
# Build and start the server
./scripts/run_server.sh
```

### 2. Add a New Model

<model_name> is the name of the model you want to add to the Triton server.

```bash
./scripts/run_server.sh --model <model_name>

# Example:
./scripts/run_server.sh --model asia-new-bay-l-v2-ct
```

### 3. Download Model Weights

Place your model weights into `models/<model_name>/faster-whisper-model/`.

You can use the helper script to download from Hugging Face:

```bash
# Usage: ./scripts/download_model.sh <repo_id> <destination_path>

# Example:
# Official Model
./scripts/download_model.sh systran/faster-whisper-large-v3 models/<model_name>/faster-whisper-model
# Custom Model
./scripts/download_model.sh jeff7522553/asia-new-bay-l-v2-ct models/asia-new-bay-l-v2-ct/faster-whisper-model
```

*Ensure `huggingface_hub` is installed if running locally.*

### 4. Restart Server

```bash
docker compose restart
```

### 5. Test Inference

Use the provided python script to test:

```bash
# Install tritonclient if not present
pip install tritonclient[http]

# Run test (generates dummy audio if file not provided)
python3 scripts/test_inference.py --model <model_name> --audio <audio_path>

# Example:
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio test.wav
```

## Customization

-   **Dependencies**: Valid Python packages are defined in `Dockerfile` under the `micromamba` installation section.
-   **Model Logic**: The inference logic is in `models/<model_name>/1/model.py`. You can modify `TritonPythonModel` class to change how audio is processed or how the model is called.
