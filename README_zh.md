# ASR Triton Service (中文說明)

本專案提供了一個基於 `faster-whisper` 的獨立 Triton 推論伺服器 (Triton Inference Server) 設置，專門用於 ASR (自動語音辨識)。

## 目錄結構

```
asr-triton-service/
├── Dockerfile              # Docker 映像檔定義
├── docker-compose.yml      # 本地部署配置
├── models/                 # 模型儲存庫 (Model repository)
│   └── whisper_template/   # 用於新增模型的範本
└── scripts/                # 輔助腳本
```

## 快速開始

### 1. 建置並執行

```bash
# 建置映像檔並啟動伺服器
./scripts/run_server.sh
```

### 2. 新增模型

若要新增一個模型 (例如：`whisper_large_v3`)：

1.  **複製範本**：
    ```bash
    cp -r models/whisper_template models/whisper_large_v3
    ```

2.  **下載模型權重**：
    您可以使用輔助腳本從 Hugging Face 下載：
    ```bash
    # 如果需要，先安裝下載腳本的依賴 (huggingface_hub)
    pip install huggingface_hub
    # 用法：./scripts/download_model.sh <repo_id> <destination_path>
    # 例如下載官方 large-v3:
    ./scripts/download_model.sh systran/faster-whisper-large-v3 models/whisper_large_v3/faster-whisper-model
    # 或下載您指定的模型:
    # ./scripts/download_model.sh jeff7522553/asia-new-bay-l-v2-ct models/asia-new-bay-l-v2-ct/faster-whisper-model
    ```
    *或者，您可以手動將 `faster-whisper-model` 資料夾 (包含 `model.bin`, `config.json` 等檔案) 放入 `models/whisper_large_v3/` 中。*

3.  **更新設定**：
    編輯 `models/whisper_large_v3/config.pbtxt`：
    -   將 `name: "whisper_template"` 修改為 `name: "whisper_large_v3"`。
    -   (選用) 調整 `instance_group` 以設定 GPU 使用量。

4.  **重新啟動伺服器**：
    ```bash
    docker compose restart
    ```

### 3. 測試推論

使用提供的 Python 腳本進行測試：

```bash
# 若尚未安裝 tritonclient
pip install tritonclient[http]

# 執行測試 (若未提供音檔路徑，將生成靜音測試)
python3 scripts/test_inference.py --model whisper_large_v3
```

## 自定義與修改

-   **依賴套件**：有效的 Python 套件定義在 `Dockerfile` 中的 `micromamba` 安裝區塊。
-   **模型邏輯**：推論邏輯位於 `models/<model_name>/1/model.py`。您可以修改 `TritonPythonModel` 類別來變更音訊處理方式或模型呼叫方式。
