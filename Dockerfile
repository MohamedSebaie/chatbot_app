FROM nvidia/cuda:12.1.1-devel-ubuntu22.04
# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
# Install system dependencies
RUN apt-get update && apt-get install -y \
   python3.10 \
   python3-pip \
   git \
   wget \
   ninja-build \
   build-essential \
&& rm -rf /var/lib/apt/lists/*
# Set working directory
WORKDIR /app
# Upgrade pip
RUN python3 -m pip install --upgrade pip
# Install specific versions of PyTorch and related packages
RUN pip3 install --no-cache-dir \
   torch==2.0.1+cu118 \
   torchvision==0.15.2+cu118 \
   --extra-index-url https://download.pytorch.org/whl/cu118
# Install CUDA toolkit specifically for 12.1
RUN cd /tmp && \
   wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_530.30.02_linux.run && \
   chmod +x cuda_12.1.1_530.30.02_linux.run && \
   ./cuda_12.1.1_530.30.02_linux.run --toolkit --silent --override && \
   rm cuda_12.1.1_530.30.02_linux.run
# Create symlinks for CUDA libraries
RUN ln -sf /usr/local/cuda/lib64/libcusparse.so.12 /usr/local/cuda/lib64/libcusparse.so && \
   ln -sf /usr/local/cuda/lib64/libnvJitLink.so.12 /usr/local/cuda/lib64/libnvJitLink.so
# Install vLLM dependencies
RUN pip3 install --no-cache-dir \
   ninja \
   packaging \
   psutil \
   ray \
   sentencepiece \
   numpy \
   transformers \
   fastapi \
   uvicorn \
   pydantic
# Install specific vLLM version
RUN pip3 install --no-cache-dir https://vllm-wheels.s3.us-west-2.amazonaws.com/nightly/vllm-1.0.0.dev-cp38-abi3-manylinux1_x86_64.whl
# Verify installations
RUN python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda)" && \
   python3 -c "from vllm import LLM; print('vLLM imported successfully')"
# Copy requirements and install other dependencies
COPY requirements.txt .
RUN sed -i '/torch/d' requirements.txt && \
   sed -i '/vllm/d' requirements.txt && \
   pip3 install --no-cache-dir -r requirements.txt
# Copy the application code
COPY . .
# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/vector_store
# Expose ports
EXPOSE 8000 8080 8501
# Start services
CMD ["python3", "scripts/start_services.py"]