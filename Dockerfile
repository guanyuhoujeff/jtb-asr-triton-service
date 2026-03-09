FROM nvcr.io/nvidia/tritonserver:24.11-py3

ENV DEBIAN_FRONTEND=noninteractive

USER root

# Install Python dependencies directly in Triton's system Python
RUN pip install --no-cache-dir \
    faster-whisper==1.2.1 \
    numpy

# Set up environment
WORKDIR /opt/tritonserver
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64

CMD ["tritonserver", "--model-repository=/models", "--log-verbose=1"]
