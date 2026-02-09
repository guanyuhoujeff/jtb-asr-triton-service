# ASR Triton Service (中文說明)

本專案提供了一個基於 `faster-whisper` 的獨立 Triton 推論伺服器 (Triton Inference Server) 設置，專門用於 ASR (自動語音辨識)。

## 目錄結構

```
asr-triton-service/
├── Dockerfile              # Docker 映像檔定義
├── docker-compose.yml      # 本地部署配置
├── models/                 # 模型儲存庫 (Model repository)
├── scripts/                # 輔助腳本
└── templates/              # 模型範本
    └── whisper_template/   # 用於新增模型的範本
```

## 快速開始

### 1. 建置並執行

```bash
# 建置映像檔並啟動伺服器
./scripts/run_server.sh
```

### 2. 新增模型

<model_name> 為您要在triton server上新增的模型名稱

```bash
./scripts/run_server.sh --model <model_name>

# 例如：
./scripts/run_server.sh --model asia-new-bay-l-v2-ct
```


### 3. 下載模型權重
    將您的模型權重放入 `models/<model_name>/faster-whisper-model/`。

    您可以使用輔助腳本從 Hugging Face 下載：
    ```bash
    # 用法：./scripts/download_model.sh <repo_id> <destination_path>

    # 例如：
    # 官方模型
    ./scripts/download_model.sh systran/faster-whisper-large-v3 models/<model_name>/faster-whisper-model
    # 客製化模型
    ./scripts/download_model.sh jeff7522553/asia-new-bay-l-v2-ct models/asia-new-bay-l-v2-ct/faster-whisper-model
    ```

    *若在本地執行，請確保已安裝 `huggingface_hub`。*

### 4. 重新啟動伺服器
    ```bash
    docker compose restart
    ```

### 5. 測試推論

使用提供的 Python 腳本進行測試：

```bash
# 若尚未安裝 tritonclient
pip install tritonclient[http]

# 執行測試 (若未提供音檔路徑，將生成靜音測試)
python3 scripts/test_inference.py --model <model_name> --audio <audio_path>

# 例如：
python3 scripts/test_inference.py --model asia-new-bay-l-v2-ct --audio test.wav
```

## 自定義與修改

-   **依賴套件**：有效的 Python 套件定義在 `Dockerfile` 中的 `micromamba` 安裝區塊。
-   **模型邏輯**：推論邏輯位於 `models/<model_name>/1/model.py`。您可以修改 `TritonPythonModel` 類別來變更音訊處理方式或模型呼叫方式。
