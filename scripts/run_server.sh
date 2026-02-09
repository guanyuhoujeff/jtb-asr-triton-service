#!/bin/bash
# scripts/run_server.sh

echo "Building Docker image..."
docker compose build

echo "Starting Triton Server..."
docker compose up -d

echo "Triton Server started. Logs:"
docker compose logs -f
