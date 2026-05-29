# ASR Triton Service (中文說明)

本專案提供了一個基於 `faster-whisper` 的獨立 Triton 推論伺服器 (Triton Inference Server) 設置，專門用於 ASR (自動語音辨識)。

## 目錄結構

```
asr-triton-service/
├── Dockerfile              # Docker 映像檔定義
├── docker-compose.yml      # 本地部署配置
├── models/                 # 模型儲存庫 (Model repository)
├── scripts/                # 輔助腳本
│   ├── run_server.sh       # 建置、新增模型、啟動伺服器
│   └── test_inference.py   # 推論測試客戶端
└── templates/              # 模型範本
    └── whisper_template/   # 用於新增模型的範本
```

## 事前準備（首次使用必裝）

執行 `run_server.sh` 之前，請先確認下列環境已安裝，否則腳本會中途報錯：

```bash
# 1. Python 套件 huggingface_hub（腳本下載模型權重時使用）
pip install huggingface_hub

# 2. Docker Compose v2 外掛（腳本以 `docker compose` 指令建置/啟動）
sudo apt-get update
# 視 Docker 安裝來源擇一：
#   (a) 用 Ubuntu 內建源安裝的 docker.io → 套件名為 docker-compose-v2
sudo apt-get install -y docker-compose-v2
#   (b) 用 Docker 官方源安裝的 docker-ce → 套件名為 docker-compose-plugin
# sudo apt-get install -y docker-compose-plugin
docker compose version   # 驗證安裝成功
```

> **常見錯誤對照**
> - `ModuleNotFoundError: No module named 'huggingface_hub'` → 未安裝 `huggingface_hub`，執行上方第 1 步。
> - `docker: unknown command: docker compose` → 未安裝 Docker Compose v2 外掛，執行上方第 2 步。

此外，`docker-compose.yml` 預設要求 **NVIDIA GPU**（`driver: nvidia, count: 1`），請確認：

- 已安裝 NVIDIA 驅動，`nvidia-smi` 可正常顯示 GPU。
- 已安裝 [`nvidia-container-toolkit`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)，讓 Docker 容器能存取 GPU。

## 快速開始

### 1. 啟動伺服器

```bash
# 啟動伺服器（模型須已存在）
./scripts/run_server.sh

# 建置 Docker 映像檔並啟動伺服器
./scripts/run_server.sh --build
```

### 2. 新增模型

`<model_name>` 為您要在 Triton server 上新增的模型名稱，`<hf_repo_id>` 為 HuggingFace 上的模型 repo ID。

```bash
./scripts/run_server.sh --model <model_name> --repo_id <hf_repo_id>

# 例如（首次使用，搭配 --build）：
./scripts/run_server.sh --model tvgh-l-v2-ct2 --repo_id jeff7522553/tvgh-l-v2-ct2 --build
```

此腳本會自動：
1. 從 template 建立模型目錄
2. 從 HuggingFace 下載模型權重
3. 啟動伺服器（加 `--build` 可重新建置 Docker 映像檔）

若模型已存在，步驟 1 和 2 會自動跳過。

### 3. 自訂 Port

```bash
# 自訂 HTTP port
./scripts/run_server.sh --port 9000

# 自訂全部 port
./scripts/run_server.sh --port 9000 --grpc-port 9001 --metrics-port 9002
```

預設 port：HTTP `8000`、gRPC `8001`、Metrics `8002`。

### 4. 重新啟動伺服器（若需手動重啟）

```bash
docker compose restart
```

### 5. 測試推論

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行測試（若未提供音檔路徑，將生成靜音測試）
python3 scripts/test_inference.py --model <model_name> --audio <audio_path>

# 例如：
# 指定語言可獲得更好的辨識結果
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio zh-test.wav --lang zh
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio en-test.wav --lang en

# 指定不同的伺服器位址
python3 scripts/test_inference.py --url 192.168.1.100:8000 --model asia-new-bay-l-v2-ct --audio zh-test.wav
```

## 自定義與修改

-   **依賴套件**：Python 套件定義在 `Dockerfile` 中的 `pip install` 區塊。
-   **模型邏輯**：推論邏輯位於 `models/<model_name>/1/model.py`。您可以修改 `TritonPythonModel` 類別來變更音訊處理方式或模型呼叫方式。
