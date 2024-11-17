# Document ChatBot with vLLM

A powerful document chatbot that combines vLLM, FastAPI, and Streamlit to provide intelligent responses based on uploaded documents. The system supports both OpenAI GPT and Llama 3 models, featuring real-time streaming responses and conversation memory.

## Features
- 📑 Document Processing: Upload and process PDF documents
- 💬 Intelligent Chat: Context-aware responses using vLLM
- 🔍 Document Search: Semantic search using FAISS
- 🚀 High Performance: Tensor parallelism support with vLLM
- 🌐 Modern Interface: Streamlit-based UI with real-time responses
- 📚 Multi-document Support: Chat with multiple uploaded documents
- 🔄 Context Retention: Maintains conversation context (Working on it)
- 📈 Source Citations: Provides references for responses

## Demo

https://github.com/MohamedSebaie/document-chatbot/demo.mp4

For the full demonstration video, check out our [detailed walkthrough](demo.mp4).

### Features Demonstrated
- 📝 Document Upload & Processing
- 💬 Interactive Chat Interface
- 🔍 Context-Aware Responses
- 📚 Source Citations
- ⚡ Real-time Processing
  
## System Requirements
- NVIDIA Driver >= 525.60.13
- CUDA Toolkit >= 12.1
- Python 3.10+
- 16GB+ RAM
- Ubuntu 22.04 or later

## Technical Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Models**: OpenAI GPT, Llama 3
- **GPU parallelism**: vLLM
- **Vector Store**: FAISS
- **Document Processing**: PyPDF2, LangChain
- **Containerization**: Docker

## Project Structure
document-chatbot/
├── app/
│ ├── api/
│ │ └── routes.py # FastAPI routes
│ └── core/
│ ├── config.py # Configuration settings
│ ├── document_processor.py # PDF processing
│ └── exceptions.py # Custom exceptions
│ ├── llm_manager.py # LLM integration
│ └── memory_manager.py # Conversation memory
├── frontend/
├── components/
│   ├── chat_interface.py # Streamlit chat interface
│   ├── document_uploader.py # File upload handling
    ├── model_selector.py # File model selector
│ └── app.py # Streamlit application
├── scripts/
│ └── start_services.py # Service orchestration
├── data/
│ ├── uploads/ # Document storage
│ └── vector_store/ # FAISS indexes
├── Dockerfile
├── docker-compose.yml
├── vllm_env.yaml # Conda environment
└── README.md

## Installation Methods

### Method 1: Direct Installation (Recommended for Development)

1. Install NVIDIA Driver and CUDA Toolkit:
```bash
# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.1-530.30.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.1-530.30.02-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/

# Install CUDA
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-1

2. Install Miniconda:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc

3. Clone the repository:
git clone https://github.com/yourusername/document-chatbot.git
cd document-chatbot

4. Create and activate conda environment:
conda env create -f vllm_env.yaml
conda activate vllm_env

5. Create necessary directories:
mkdir -p data/uploads data/vector_store

6. Start the services:
python scripts/start_services.py
```
### Method 2: Docker Installation (Recommended for Production)
```bash
1. Install Docker:

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

2. Install NVIDIA Container Toolkit:
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Docker support
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

3. Clone and build:
git clone https://github.com/yourusername/document-chatbot.git
cd document-chatbot

# Build and start services
docker-compose up --build

4. Stop services:
docker-compose down
```
## Usage
### Access the interfaces:
- Streamlit UI: http://localhost:8501
- FastAPI Docs: http://localhost:8080/docs
- vLLM API: http://localhost:8000/v1
### Upload Documents:
- Use the sidebar uploader
- Support for PDF files
- Wait for processing confirmation
### Chat Interface:
- Type questions in chat
- View source citations
- Clear chat history as needed

# License
MIT License - see LICENSE file for details

# Acknowledgments
- vLLM Team for the inference engine
- Hugging Face for model hosting
- FastAPI and Streamlit teams

# Contact
GitHub Issues: Project Issues
Email: mohamedsebaie1@gmail.com 
