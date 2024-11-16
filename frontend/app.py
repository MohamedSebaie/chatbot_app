import streamlit as st
from components.model_selector import ModelSelector
from components.document_uploader import DocumentUploader
from components.chat_interface import ChatInterface
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Constants
API_URL = "http://localhost:8080"
APP_TITLE = "🤖 Document ChatBot"
class ChatbotApp:
   def __init__(self):
       self.model_selector = ModelSelector()
       self.document_uploader = DocumentUploader(API_URL)
       self.chat_interface = ChatInterface(API_URL)
   def setup_page(self):
       """Configure page settings."""
       st.set_page_config(
           page_title=APP_TITLE,
           page_icon="🤖",
           layout="wide",
           initial_sidebar_state="expanded"
       )
       # Custom CSS
       st.markdown("""
<style>
           .stApp {
               max-width: 100%;
               padding-top: 1rem;
           }
           .main .block-container {
               padding-top: 2rem;
           }
           .uploadedFile {
               border: 1px solid #ccc;
               padding: 10px;
               border-radius: 5px;
               margin: 10px 0;
           }
           .document-info {
               background-color: #f0f2f6;
               padding: 1rem;
               border-radius: 10px;
               margin: 1rem 0;
           }
           .chat-message {
               padding: 1.5rem;
               border-radius: 10px;
               margin-bottom: 1rem;
           }
           .chat-message.user {
               background-color: #e6f3ff;
           }
           .chat-message.assistant {
               background-color: #f0f2f6;
           }
</style>
       """, unsafe_allow_html=True)
   def render_sidebar(self):
       """Render sidebar content."""
       with st.sidebar:
        #    st.title("Settings")
           # Model Selection
           st.header("Model Settings")
           model_type = self.model_selector.render()
           # Document Upload
           st.header("📄 Document Upload")
           self.document_uploader.render(model_type)
           # Help & Information
           with st.expander("ℹ️ Help & Information"):
               st.markdown("""
               **How to use:**
               1. Select your preferred model
               2. Upload a PDF document
               3. Ask questions about the document
               **Features:**
               - PDF document analysis
               - Real-time chat
               - Context-aware responses
               - Source citations
               """)
   def main(self):
       """Main application."""
       self.setup_page()
       # Render sidebar
       self.render_sidebar()
       # Main content area
       st.title(APP_TITLE)
       # Chat interface in main area
       self.chat_interface.render()
if __name__ == "__main__":
   try:
       app = ChatbotApp()
       app.main()
   except Exception as e:
       logger.error(f"Application error: {str(e)}")
       st.error(f"An error occurred: {str(e)}")