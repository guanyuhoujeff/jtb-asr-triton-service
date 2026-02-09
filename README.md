# ASR Triton Service

> [中文說明 (Chinese README)](README_zh.md)

This project provides a standalone Triton Inference Server setup for ASR (Automatic Speech Recognition) using `faster-whisper`.

## Directory Structure

```
asr-triton-service/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local deployment configuration
├── models/                 # Model repository
│   └── whisper_template/   # Template for adding new models
└── scripts/                # Helper scripts
```

## Getting Started

### 1. Build and Run

```bash
# Build and start the server
./scripts/run_server.sh
```

### 2. Add a New Model

To add a new model (e.g., `whisper_large_v3`):

1.  **Copy the template**:
    ```bash
    cp -r models/whisper_template models/whisper_large_v3
    ```

2.  **Download Model Weights**:
    You can use the helper script to download from Hugging Face:
    ```bash
    # Install dependencies for download script if needed (huggingface_hub)
    pip install huggingface_hub
    # Usage: ./scripts/download_model.sh <repo_id> <destination_path>
    ./scripts/download_model.sh systran/faster-whisper-large-v3 models/whisper_large_v3/faster-whisper-model
    ```
    *Alternatively, manually place the `faster-whisper-model` directory (containing `model.bin`, `config.json`, etc.) inside `models/whisper_large_v3/`.*

3.  **Update Configuration**:
    Edit `models/whisper_large_v3/config.pbtxt`:
    -   Change `name: "whisper_template"` to `name: "whisper_large_v3"`.
    -   (Optional) Adjust `instance_group` for more GPU instances.

4.  **Restart Server**:
    ```bash
    docker-compose restart
    ```

### 3. Test Inference

Use the provided python script to test:

```bash
# Install tritonclient if not present
pip install tritonclient[http]

# Run test (generates dummy audio if file not provided)
python3 scripts/test_inference.py --model whisper_large_v3
```

## Customization

-   **Dependencies**: Valid Python packages are defined in `Dockerfile` under the `micromamba` installation section.
-   **Model Logic**: The inference logic is in `models/<model_name>/1/model.py`. You can modify `TritonPythonModel` class to change how audio is processed or how the model is called.
