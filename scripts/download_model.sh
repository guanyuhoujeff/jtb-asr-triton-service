#!/bin/bash
# scripts/download_model.sh
# Usage: ./scripts/download_model.sh <repo_id> <destination_folder>
# Example: ./scripts/download_model.sh jeff7522553/asia-new-bay-l-v2-ct ./models/asia-new-bay-l-v2-ct/faster-whisper-model

REPO_ID=$1
DEST_DIR=$2

if [ -z "$REPO_ID" ] || [ -z "$DEST_DIR" ]; then
    echo "Usage: $0 <repo_id> <destination_folder>"
    echo "Example: $0 jeff7522553/asia-new-bay-l-v2-ct ./models/asia-new-bay-l-v2-ct/faster-whisper-model"
    exit 1
fi

echo "Downloading $REPO_ID to $DEST_DIR..."
mkdir -p "$DEST_DIR"

# Using python to download via huggingface_hub
python3 -c "
from huggingface_hub import snapshot_download
import sys

model_id = '${REPO_ID}'
dest = '${DEST_DIR}'

print(f'Downloading {model_id} to {dest}...')
snapshot_download(repo_id=model_id, local_dir=dest)
"

echo "Download complete."
