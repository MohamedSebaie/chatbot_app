from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
from fastapi import APIRouter, UploadFile
import numpy as np
import pickle
import os
import io
from PyPDF2 import PdfReader
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)
class DocumentProcessor:
   def __init__(self) -> None:
       self.text_splitter = RecursiveCharacterTextSplitter(
           chunk_size=1000,
           chunk_overlap=200,
           length_function=len
       )
       self.embeddings = HuggingFaceEmbeddings(
           model_name="intfloat/multilingual-e5-large"
       )
       self.vector_store = None
       self.vector_store_path = "data/vector_store"
   async def process_document(self, file: UploadFile, filename: str) -> List[Dict]:
        try:
            # Read and process PDF
            contents = await file.read()
            pdf_file = io.BytesIO(contents)
            pdf_reader = PdfReader(pdf_file)
            text_chunks = []
            metadata_chunks = []
            # Extract text and create chunks
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                # print('===============================================')
                # print('page_num: ',page_num)
                # print('===============================================')
                # print(text)
                if text.strip():
                    chunks = self.text_splitter.split_text(text)
                    for chunk_num, chunk in enumerate(chunks):
                        text_chunks.append(chunk)
                        metadata_chunks.append({
                            "source": filename,
                            "page": page_num + 1,
                            "chunk": chunk_num + 1,
                            "total_pages": len(pdf_reader.pages)
                        })
            # Process vectors and store them
            if text_chunks:  # Only process if we have chunks
                # Create embeddings
                embeddings = self.embeddings.embed_documents(text_chunks)
                # Save to vector store
                os.makedirs(self.vector_store_path, exist_ok=True)
                # Initialize or update FAISS index
                index = None
                if os.path.exists(os.path.join(self.vector_store_path, "index.faiss")):
                    index = faiss.read_index(os.path.join(self.vector_store_path, "index.faiss"))
                    index.add(np.array(embeddings))
                else:
                    index = faiss.IndexFlatL2(len(embeddings[0]))
                    index.add(np.array(embeddings))
                # Save index
                faiss.write_index(index, os.path.join(self.vector_store_path, "index.faiss"))
                # Save metadata and texts
                with open(os.path.join(self.vector_store_path, "metadata.pkl"), 'wb') as f:
                    pickle.dump(metadata_chunks, f)
                with open(os.path.join(self.vector_store_path, "texts.pkl"), 'wb') as f:
                    pickle.dump(text_chunks, f)
            # Return processed chunks with metadata
            return [
                {
                    "content": text,
                    "metadata": metadata
                }
                for text, metadata in zip(text_chunks, metadata_chunks)
            ]
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process PDF: {str(e)}"
            )
   async def get_relevant_chunks(self, query: str, k: int = 3) -> List[Dict]:
       """Retrieve relevant document chunks for a query."""
       try:
           index_path = os.path.join(self.vector_store_path, "index.faiss")
           metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
           texts_path = os.path.join(self.vector_store_path, "texts.pkl")
           if not all(os.path.exists(p) for p in [index_path, metadata_path, texts_path]):
               return []
           # Load index and data
           index = faiss.read_index(index_path)
           with open(metadata_path, 'rb') as f:
               metadata = pickle.load(f)
           with open(texts_path, 'rb') as f:
               texts = pickle.load(f)
           # Get query embedding
           query_embedding = self.embeddings.embed_query(query)
           # Search
           D, I = index.search(np.array([query_embedding]), k)
           # Format results
           results = []
           for score, idx in zip(D[0], I[0]):
               if idx < len(texts) and idx < len(metadata):
                   results.append({
                       "content": texts[idx],
                       "metadata": metadata[idx],
                       "score": float(score)
                   })
           return results
       except Exception as e:
           logger.error(f"Error retrieving chunks: {str(e)}")
           return []
   async def validate_file(self, file: UploadFile, filename: str) -> bool:
       """Validate the uploaded file."""
       if not filename.lower().endswith('.pdf'):
           raise HTTPException(
               status_code=400,
               detail="Only PDF files are allowed"
           )
       if not file.content_type == "application/pdf":
           raise HTTPException(
               status_code=400,
               detail="Invalid file type. Please upload a PDF file"
           )
       return True