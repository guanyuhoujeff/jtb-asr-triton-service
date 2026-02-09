FROM nvcr.io/nvidia/tritonserver:24.11-py3

ENV DEBIAN_FRONTEND=noninteractive
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH=$MAMBA_ROOT_PREFIX/bin:$PATH

# 1. Install system dependencies and Micromamba
USER root
RUN apt-get update && apt-get install -y wget bzip2 && rm -rf /var/lib/apt/lists/*

# Install Micromamba
RUN wget -qO- https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba \
    && mv bin/micromamba /usr/local/bin/ \
    && mkdir -p $MAMBA_ROOT_PREFIX && chmod -R 777 $MAMBA_ROOT_PREFIX

# 2. 建立 Python 3.11.6 環境
# 我們指定環境名稱為 whisper_env，因為設定了 PREFIX，它會位於 /opt/conda/envs/whisper_env
RUN micromamba create -y -n whisper_env \
    python=3.11.6 \
    pip \
    && micromamba clean --all --yes

# 3. 在該環境中安裝套件
# 使用 micromamba run -n whisper_env 確保 pip 是安裝在該環境內
RUN micromamba run -n whisper_env pip install --no-cache-dir \
    faster-whisper==1.2.1 \
    tritonclient[all] \
    conda-pack \
    torch \
    numpy

# 4. 打包環境 (關鍵修正步驟)
WORKDIR /opt/tritonserver

# 這裡不使用 -n whisper_env，改用 -p 指定絕對路徑
# 這樣 conda-pack 就不會嘗試呼叫 'conda' 指令來解析名稱
RUN micromamba run -n whisper_env conda-pack \
    -p /opt/conda/envs/whisper_env \
    -o python_env.tar.gz

# 5. 設置必要的環境變數
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
RUN pip install faster-whisper
# 6. 權限設定
RUN chmod 644 /opt/tritonserver/python_env.tar.gz

CMD ["tritonserver", "--model-repository=/models"]