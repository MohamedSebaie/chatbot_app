from openai import OpenAI
from typing import Dict, List, Optional
from app.core.config import get_settings
import logging
logger = logging.getLogger(__name__)
settings = get_settings()
class LLMManager:
    def __init__(self, model_type: str = "openai"):
        """Initialize LLM manager."""
        self.model_type = model_type
        if model_type == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:  # llama/vllm
            self.client = OpenAI(
                base_url="http://localhost:8000/v1",
                api_key="not-needed"
            )
    def get_response(
        self,
        prompt: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        relevant_chunks: List[Dict] = None
    ) -> str:
        """Get response from selected model."""
        try:
            # Format context from relevant chunks
            if relevant_chunks:
                context_text = "\n\n".join([
                    f"Document: {chunk['metadata']['source']}, "
                    f"Page: {chunk['metadata']['page']}\n"
                    f"{chunk['content']}"
                    for chunk in relevant_chunks
                ])
            else:
                context_text = context
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": system_prompt or f"""You are a helpful AI assistant. Use the following context to answer the question.
                    If the answer cannot be found in the context, say so.
                    Context:
                    {context_text}
                    Answer the question based on the context above. Be specific and cite the source document and page when possible."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            # Generate completion
            completion = self.client.chat.completions.create(
                model="NousResearch/Meta-Llama-3-8B-Instruct" if self.model_type != "openai" else "gpt-3.5-turbo",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 512
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            raise
    def format_prompt(self, question: str, context: str = "") -> str:
        """Format prompt with optional context."""
        if context:
            return f"Context: {context}\n\nQuestion: {question}"
        return question

    @staticmethod
    def format_chat_history(messages: List[Dict[str, str]]) -> str:
        """Format chat history for context."""
        formatted = []
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)