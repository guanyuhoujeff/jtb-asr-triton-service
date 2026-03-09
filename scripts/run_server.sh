#!/bin/bash
# scripts/run_server.sh
# Usage:
#   僅啟動（已有模型）:
#     ./scripts/run_server.sh
#   新增模型並下載權重後啟動:
#     ./scripts/run_server.sh --model <model_name> --repo_id <hf_repo_id>
#   自訂 HTTP port:
#     ./scripts/run_server.sh --port 9000

set -e

# ── 取得專案根目錄（即 scripts/ 的上一層）──────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODELS_DIR="$PROJECT_ROOT/models"
TEMPLATE_DIR="$PROJECT_ROOT/templates/whisper_template"

# ── 解析參數 ────────────────────────────────────────────────────────────
MODEL_NAME=""
REPO_ID=""
HTTP_PORT="8000"
GRPC_PORT="8001"
METRICS_PORT="8002"
DO_BUILD=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model)        MODEL_NAME="$2";   shift ;;
        --repo_id)      REPO_ID="$2";      shift ;;
        --port)         HTTP_PORT="$2";     shift ;;
        --grpc-port)    GRPC_PORT="$2";     shift ;;
        --metrics-port) METRICS_PORT="$2";  shift ;;
        --build)        DO_BUILD=true       ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 [--model <model_name>] [--repo_id <hf_repo_id>] [--port <http_port>] [--grpc-port <grpc_port>] [--metrics-port <metrics_port>] [--build]"
            exit 1
            ;;
    esac
    shift
done

# ── 參數驗證：--model 與 --repo_id 必須同時提供或同時不提供 ─────────────
if [ -n "$MODEL_NAME" ] && [ -z "$REPO_ID" ]; then
    echo "Error: --model 需搭配 --repo_id 一起使用"
    echo "Usage: $0 --model <model_name> --repo_id <hf_repo_id>"
    exit 1
fi
if [ -z "$MODEL_NAME" ] && [ -n "$REPO_ID" ]; then
    echo "Error: --repo_id 需搭配 --model 一起使用"
    echo "Usage: $0 --model <model_name> --repo_id <hf_repo_id>"
    exit 1
fi

# ── Step 1：確認 models 資料夾存在 ─────────────────────────────────────
echo "================================================================"
if [ ! -d "$MODELS_DIR" ]; then
    echo "[1/4] models/ 不存在，建立中..."
    mkdir -p "$MODELS_DIR"
else
    echo "[1/4] models/ 已存在，略過建立。"
fi

# ── Step 2：複製 template 並更新設定 ────────────────────────────────────
if [ -n "$MODEL_NAME" ]; then
    NEW_MODEL_PATH="$MODELS_DIR/$MODEL_NAME"
    CONFIG_PATH="$NEW_MODEL_PATH/config.pbtxt"
    WEIGHTS_PATH="$NEW_MODEL_PATH/faster-whisper-model"

    echo "----------------------------------------------------------------"
    # 確認 template 存在
    if [ ! -d "$TEMPLATE_DIR" ]; then
        echo "Error: Template 不存在：$TEMPLATE_DIR"
        exit 1
    fi

    if [ -d "$NEW_MODEL_PATH" ]; then
        echo "[2/4] 模型 '$MODEL_NAME' 已存在，略過複製 template。"
    else
        echo "[2/4] 複製 template → $NEW_MODEL_PATH ..."
        cp -r "$TEMPLATE_DIR" "$NEW_MODEL_PATH"

        # 更新 config.pbtxt 中的模型名稱
        if [ -f "$CONFIG_PATH" ]; then
            sed -i "s/name: \"whisper_template\"/name: \"$MODEL_NAME\"/" "$CONFIG_PATH"
            echo "      config.pbtxt 已更新（model name → $MODEL_NAME）"
        else
            echo "Warning: 找不到 config.pbtxt，請手動確認設定。"
        fi
        echo "      模型目錄建立完成：$NEW_MODEL_PATH"
    fi

    # ── Step 3：從 HuggingFace 下載模型權重 ───────────────────────────
    echo "----------------------------------------------------------------"
    if [ -d "$WEIGHTS_PATH" ] && [ "$(ls -A "$WEIGHTS_PATH" 2>/dev/null)" ]; then
        echo "[3/4] 模型權重已存在（$WEIGHTS_PATH），略過下載。"
    else
        echo "[3/4] 從 HuggingFace 下載模型權重..."
        echo "      repo_id : $REPO_ID"
        echo "      目標路徑: $WEIGHTS_PATH"
        mkdir -p "$WEIGHTS_PATH"
        python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='${REPO_ID}', local_dir='${WEIGHTS_PATH}')
print('下載完成。')
"
    fi
else
    echo "[2/4] 未指定 --model / --repo_id，略過 template 複製與模型下載。"
    echo "[3/4] （略過）"
fi

# ── Step 4：建置並啟動 Triton Server ───────────────────────────────────
echo "================================================================"
if [ "$DO_BUILD" = true ]; then
    echo "[4/4] 建置 Docker 映像..."
    docker compose -f "$PROJECT_ROOT/docker-compose.yml" build
else
    echo "[4/4] 略過建置（如需重新建置請加 --build）"
fi

echo "[4/4] 啟動 Triton Server（HTTP=$HTTP_PORT, gRPC=$GRPC_PORT, Metrics=$METRICS_PORT）..."
export HTTP_PORT GRPC_PORT METRICS_PORT
docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d

echo "================================================================"
echo "Triton Server 已啟動，輸出 logs："
docker compose -f "$PROJECT_ROOT/docker-compose.yml" logs -f
