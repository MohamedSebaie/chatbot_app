import streamlit as st
import requests
from typing import Generator
import logging
import streamlit as st
import requests
from typing import Optional
import json
logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self, api_url: str):
        self.api_url = api_url
        if "messages" not in st.session_state:
            st.session_state.messages = []
    def clear_chat(self):
        st.session_state.messages = []
    def format_response(self, text: str) -> str:
        """Format the response text into bullet points if needed."""
        # Split the text by bullet points if they exist
        if "•" in text:
            points = [point.strip() for point in text.split("•") if point.strip()]
            formatted_text = "\n".join(f"• {point}" for point in points)
            return formatted_text
        return text
    def send_message(
        self,
        question: str,
        model_type: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Optional[dict]:
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                params={
                    "question": question,
                    "model_type": model_type,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return None
    def render(self):
        st.header("💬 Chat")
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.markdown(message["content"])
                else:
                    # Format and display the assistant's response
                    response_text = self.format_response(message["content"])
                    st.markdown(response_text)
                    # Display sources in an expander if available
                    if "sources" in message and message["sources"]:
                        with st.expander("📚 Sources"):
                            for source in message["sources"]:
                                st.markdown(
                                    f"**Document:** {source['source']}\n"
                                    f"**Page:** {source['page']}\n"
                                    f"**Relevance Score:** {source['score']:.2f}"
                                )
        # Chat input
        if question := st.chat_input("What would you like to know about the documents?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": question})
            # Display user message
            with st.chat_message("user"):
                st.markdown(question)
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.send_message(question, "llama")  # or get model_type from state
                    if response:
                        # Format and display the response
                        response_text = self.format_response(response["response"])
                        st.markdown(response_text)
                        # Display sources if available
                        if response.get("sources"):
                            with st.expander("📚 Sources"):
                                for source in response["sources"]:
                                    st.markdown(
                                        f"**Document:** {source['source']}\n"
                                        f"**Page:** {source['page']}\n"
                                        f"**Relevance Score:** {source['score']:.2f}"
                                    )
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["response"],
                            "sources": response.get("sources", [])
                        })
        # Add custom CSS for better formatting
        st.markdown("""
    <style>
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            white-space: pre-wrap;
        }
        .chat-message ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        .chat-message li {
            margin-bottom: 0.5rem;
        }
        .chat-message code {
            background-color: #f0f2f6;
            padding: 0.2rem 0.4rem;
            border-radius: 0.2rem;
        }
    </style>
        """, unsafe_allow_html=True)

    def handle_error_response(self, response: requests.Response) -> str:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            error_message = error_data.get('detail', 'Unknown error occurred')
            
            if response.status_code == 400:
                return f"Invalid request: {error_message}"
            elif response.status_code == 413:
                return f"File too large: {error_message}"
            elif response.status_code == 500:
                return f"Server error: {error_message}"
            else:
                return f"Error: {error_message}"
        except Exception:
            return f"Error: Status code {response.status_code}"

    def process_chat_response(self, response: requests.Response) -> Generator[str, None, None]:
        """Process streaming chat response with error handling."""
        if response.status_code != 200:
            error_message = self.handle_error_response(response)
            yield error_message
            return

        for line in response.iter_lines():
            if line:
                if line.startswith(b'data: '):
                    token = line[6:].decode('utf-8')
                    if token == "[DONE]":
                        break
                    yield token + " "

    def _display_message(self, message: dict) -> None:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def display_chat_history(self) -> None:
        for message in st.session_state.messages:
            self._display_message(message)

    def clear_chat(self) -> None:
        st.session_state.messages = []
        st.session_state.error_displayed = False