from fastapi import HTTPException
from typing import Any, Dict, Optional

class ChatBotException(HTTPException):
    """Base exception for ChatBot API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class DocumentProcessingError(ChatBotException):
    """Raised when document processing fails."""
    
    def __init__(
        self,
        detail: str = "Failed to process document",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class ModelNotFoundError(ChatBotException):
    """Raised when specified model is not available."""
    
    def __init__(
        self,
        detail: str = "Model not found or not supported",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=404, detail=detail, headers=headers)

class InvalidFileError(ChatBotException):
    """Raised when uploaded file is invalid."""
    
    def __init__(
        self,
        detail: str = "Invalid file format",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=400, detail=detail, headers=headers)

class FileSizeLimitError(ChatBotException):
    """Raised when file size exceeds limit."""
    
    def __init__(
        self,
        detail: str = "File size exceeds limit",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=413, detail=detail, headers=headers)

class ModelInitializationError(ChatBotException):
    """Raised when LLM initialization fails."""
    
    def __init__(
        self,
        detail: str = "Failed to initialize language model",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class MemoryManagerError(ChatBotException):
    """Raised when memory operations fail."""
    
    def __init__(
        self,
        detail: str = "Memory manager operation failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class VectorStoreError(ChatBotException):
    """Raised when vector store operations fail."""
    
    def __init__(
        self,
        detail: str = "Vector store operation failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class APIKeyError(ChatBotException):
    """Raised when API key is missing or invalid."""
    
    def __init__(
        self,
        detail: str = "Invalid or missing API key",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=401, detail=detail, headers=headers)

class RateLimitError(ChatBotException):
    """Raised when API rate limit is exceeded."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=429, detail=detail, headers=headers)

class StreamingError(ChatBotException):
    """Raised when streaming response fails."""
    
    def __init__(
        self,
        detail: str = "Streaming response failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class ValidationError(ChatBotException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        detail: str = "Input validation failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=422, detail=detail, headers=headers)

class DatabaseError(ChatBotException):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        detail: str = "Database operation failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=500, detail=detail, headers=headers)

class AuthenticationError(ChatBotException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=401, detail=detail, headers=headers)

class AuthorizationError(ChatBotException):
    """Raised when user is not authorized."""
    
    def __init__(
        self,
        detail: str = "Not authorized",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=403, detail=detail, headers=headers)

def handle_exception(e: Exception) -> ChatBotException:
    """
    Convert generic exceptions to ChatBotException.
    
    Args:
        e: The exception to handle
        
    Returns:
        ChatBotException: Appropriate ChatBot exception
    """
    if isinstance(e, ChatBotException):
        return e
        
    error_mapping = {
        ValueError: ValidationError,
        KeyError: ValidationError,
        FileNotFoundError: InvalidFileError,
        PermissionError: AuthorizationError,
        ConnectionError: DatabaseError,
        TimeoutError: RateLimitError
    }
    
    exception_class = error_mapping.get(type(e), ChatBotException)
    return exception_class(detail=str(e))

def is_critical_error(error: ChatBotException) -> bool:
    """
    Check if an error is critical and requires immediate attention.
    
    Args:
        error: The error to check
        
    Returns:
        bool: True if error is critical
    """
    critical_status_codes = {500, 503, 504}
    return error.status_code in critical_status_codes

def get_user_friendly_message(error: ChatBotException) -> str:
    """
    Get user-friendly error message.
    
    Args:
        error: The error to get message for
        
    Returns:
        str: User-friendly error message
    """
    status_messages = {
        400: "There was a problem with your request. Please check the input and try again.",
        401: "Authentication failed. Please check your credentials.",
        403: "You don't have permission to perform this action.",
        404: "The requested resource was not found.",
        413: "The file you're trying to upload is too large.",
        422: "The provided data is invalid.",
        429: "Too many requests. Please try again later.",
        500: "An internal server error occurred. Our team has been notified.",
        503: "The service is temporarily unavailable. Please try again later."
    }
    
    return status_messages.get(
        error.status_code,
        "An unexpected error occurred. Please try again."
    )