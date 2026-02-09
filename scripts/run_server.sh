#!/bin/bash
# scripts/run_server.sh

# Parse arguments
MODEL_NAME=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model) MODEL_NAME="$2"; shift ;;
        *) ;;
    esac
    shift
done

# If a model name is provided, create the model
if [ -n "$MODEL_NAME" ]; then
    echo "Creating new model: $MODEL_NAME"
    python3 scripts/add_model.py --name "$MODEL_NAME"
    if [ $? -ne 0 ]; then
        echo "Failed to create model $MODEL_NAME"
        exit 1
    fi
fi

echo "Building Docker image..."
docker compose build

echo "Starting Triton Server..."
docker compose up -d

echo "Triton Server started. Logs:"
docker compose logs -f
