from pydantic_settings import BaseSettings
from typing import Optional, List, ClassVar
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings and configuration.
    """
    
    # Basic Settings
    PROJECT_NAME: str = "Document ChatBot"
    DEBUG: bool = False
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = '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'
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    SENTENCE_TRANSFORMER_PATH: str = r"models/sentence_transformer/multilingual-e5-large"
    
    # vLLM Settings
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_API_KEY: str = "token-abc123"
    VLLM_MODEL_PATH: str = "models/llama"
    VLLM_MAX_MODEL_LEN: int = 4096
    VLLM_GPU_MEMORY_UTILIZATION: float = 0.85
    
    # Model Selection
    DEFAULT_MODEL_TYPE: str = "llama"  # or "llama"
    
    # File Upload Settings
    UPLOAD_DIR: Path = Path("data/uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Server Settings
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    STREAMLIT_PORT: int = 8501
    
    # Security Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:8000"]
    API_KEY_HEADER: str = "X-API-Key"
    
    # Vector Store Settings
    VECTOR_STORE_PATH: str = "data/vector_store"
    EMBEDDING_MODEL: str = "models/sentence_transformer\multilingual-e5-large"
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600

    # Constants (not settings)
    DEFAULT_CHUNK_SIZE: ClassVar[int] = 1000
    DEFAULT_CHUNK_OVERLAP: ClassVar[int] = 200

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "allow"

    def validate_paths(self) -> None:
        """Ensure required directories exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        Path(self.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)
        
        # # Validate model paths
        # if self.MODEL_TYPE == "llama":
        #     llama_path = Path(self.LLAMA_MODEL_PATH)
        #     if not llama_path.exists():
        #         raise ValueError(f"Llama model not found at {llama_path}")
        
        # # Validate sentence transformer path
        # print(Path(self.SENTENCE_TRANSFORMER_PATH))
        # transformer_path = Path(self.SENTENCE_TRANSFORMER_PATH)
        # if not transformer_path.exists():
        #     raise ValueError(f"Sentence transformer model not found at {transformer_path}")

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate_paths()
    return settings