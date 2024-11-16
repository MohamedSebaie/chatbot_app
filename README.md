# Document ChatBot

## Overview
An advanced document chatbot system that allows users to upload PDF documents and interact with them using state-of-the-art language models. The system supports both OpenAI GPT and Llama 2 models, featuring real-time streaming responses and conversation memory.

## Features
- 📄 PDF document processing and analysis
- 💬 Real-time chat with streaming responses
- 🔄 Multiple model support (OpenAI GPT and Llama 2)
- 🧠 Conversation memory and context awareness
- 📱 Responsive web interface
- 🔒 Local deployment option
- 🐳 Docker support

## Technical Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Models**: OpenAI GPT, Llama 2
- **Vector Store**: FAISS
- **Document Processing**: PyPDF2, LangChain
- **Containerization**: Docker

## Environment Variables

The application uses the following environment variables. Copy `.env.example` to `.env` and adjust the values:

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_TYPE`: Type of LLM to use (`openai` or `llama`)

### Optional Variables
- `DEBUG`: Enable debug mode (`true` or `false`)
- `LLAMA_MODEL_PATH`: Path to Llama model files
- `MAX_FILE_SIZE`: Maximum allowed file size in bytes
- `UPLOAD_DIR`: Directory for temporary file storage
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT`: Deployment environment (development, production)

### Example Setup
```bash
# Create environment file
cp .env.example .env

# Edit the file with your values
nano .env

## Quick Start

### Using Docker
```bash
# Clone the repository
git clone https://github.com/yourusername/document-chatbot.git
cd document-chatbot

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Build and run
docker-compose up --build