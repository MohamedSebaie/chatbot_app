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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Add conda to path
ENV PATH=/opt/conda/bin:$PATH

# Set working directory
WORKDIR /app

# Copy environment file
COPY vllm_env.yaml .

# Create conda environment
RUN conda env create -f vllm_env.yaml && \
    conda clean -afy

# Add conda environment to PATH
ENV PATH=/opt/conda/envs/vllm_env/bin:$PATH
ENV CONDA_DEFAULT_ENV=vllm_env

# Install CUDA toolkit for 12.1
RUN cd /tmp && \
    wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_530.30.02_linux.run && \
    chmod +x cuda_12.1.1_530.30.02_linux.run && \
    ./cuda_12.1.1_530.30.02_linux.run --toolkit --silent --override && \
    rm cuda_12.1.1_530.30.02_linux.run

# Create symlinks for CUDA libraries
RUN ln -sf /usr/local/cuda/lib64/libcusparse.so.12 /usr/local/cuda/lib64/libcusparse.so && \
    ln -sf /usr/local/cuda/lib64/libnvJitLink.so.12 /usr/local/cuda/lib64/libnvJitLink.so

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/vector_store

# Expose ports
EXPOSE 8000 8080 8501

# Create entrypoint script
RUN echo '#!/bin/bash\n\
source /opt/conda/etc/profile.d/conda.sh\n\
conda activate vllm_env\n\
exec python3 scripts/start_services.py\n\
' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
