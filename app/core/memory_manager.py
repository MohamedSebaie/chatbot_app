from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from app.core.config import get_settings
from app.core.exceptions import ModelInitializationError
import logging
from typing import List, Optional, Dict, Any

from typing import List, Dict
import json
logger = logging.getLogger(__name__)
settings = get_settings()

class MemoryManager:
    """Manages conversation memory and document storage."""
    
    def __init__(self, model_type: str):
        """
        Initialize memory manager.
        
        Args:
            model_type: Type of model to use (openai/llama)
        """
        self.model_type = model_type
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        try:
            self.embeddings = self._initialize_embeddings()
            self.vector_store = None
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise ModelInitializationError(f"Failed to initialize embeddings: {str(e)}")

    def _initialize_embeddings(self):
        """Initialize embeddings based on model type."""
        if self.model_type == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            return OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            # Use HuggingFace embeddings for local model
            return HuggingFaceEmbeddings(
                model_name=settings.SENTENCE_TRANSFORMER_PATH,
                model_kwargs={'device': 'cpu'}
            )

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store.
        
        Args:
            documents: List of documents to add
        """
        try:
            if not documents:
                raise ValueError("No documents provided")
                
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(
                    documents,
                    self.embeddings
                )
                logger.info("Created new vector store")
            else:
                self.vector_store.add_documents(documents)
                logger.info("Added documents to existing vector store")
                
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Get documents relevant to query.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant documents
        """
        if self.vector_store is None:
            logger.warning("No documents in vector store")
            return []
            
        return self.vector_store.similarity_search(query)

    def add_user_message(self, message: str) -> None:
        """
        Add user message to memory.
        
        Args:
            message: User message
        """
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str) -> None:
        """
        Add AI message to memory.
        
        Args:
            message: AI message
        """
        self.memory.chat_memory.add_ai_message(message)

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get chat history.
        
        Returns:
            List of chat messages
        """
        messages = []
        for msg in self.memory.chat_memory.messages:
            messages.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        return messages

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()

class ConversationMemory:
   def __init__(self):
       self.messages: List[Dict[str, str]] = []
   def add_message(self, role: str, content: str, **kwargs):
       """Add a message to the conversation history."""
       message = {"role": role, "content": content}
       message.update(kwargs)
       self.messages.append(message)
   def get_messages(self) -> List[Dict[str, str]]:
       """Get all messages in the conversation."""
       return self.messages
   def clear(self):
       """Clear the conversation history."""
       self.messages = []
   def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
       """Get the last n messages from the conversation."""
       return self.messages[-n:] if n > 0 else []