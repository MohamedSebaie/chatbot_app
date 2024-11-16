import streamlit as st
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def upload_file(file, API_URL) -> Optional[dict]:
   if file is None:
       return None
   try:
       # Create file upload payload
       files = {"file": (file.name, file.getvalue(), "application/pdf")}
       # Send POST request to upload endpoint
       response = requests.post(
           f"{API_URL}/upload",
           files=files,
           timeout=60  # Increased timeout for large files
       )
       # Check response
       response.raise_for_status()
       return response.json()
   except requests.exceptions.RequestException as e:
       st.error(f"Upload failed: {str(e)}")
       return None

class DocumentUploader:
    """Component for document upload handling."""
    
    def __init__(self, api_url: str):
        self.api_url = api_url

    def render(self, model_type: str) -> Optional[bool]:
        """
        Render document upload component.
        
        Args:
            model_type: Current model type
            
        Returns:
            Boolean indicating upload success
        """
        # st.subheader("📄 Document Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to chat about"
        )

        if uploaded_file:
            try:
                with st.spinner("Processing document..."):
                    result = upload_file(uploaded_file, self.api_url)
                    if result:
                        st.success(f"""
                        Document processed successfully!
                        - Filename: {result['filename']}
                        - Pages: {result['pages']}
                        - Text chunks: {result['chunks']}
                        """)
                        
                            
            except Exception as e:
                logger.error(f"Error uploading document: {str(e)}")
                st.error(f"❌ Error uploading document: {str(e)}")
                return False

