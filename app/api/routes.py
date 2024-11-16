from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os
import aiofiles
from app.core.config import get_settings
from app.core.document_processor import DocumentProcessor
from app.core.llm_manager import LLMManager
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
doc_processor = DocumentProcessor()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
   try:
       # Validate file
       filename = file.filename
       await doc_processor.validate_file(file, filename)
       # Create upload directory if it doesn't exist
       upload_dir = Path(settings.UPLOAD_DIR)
       upload_dir.mkdir(parents=True, exist_ok=True)
       # Process the document
       documents = await doc_processor.process_document(file, filename)
       # Get number of pages and chunks safely
       num_chunks = len(documents) if documents else 0
       num_pages = len(set(doc['metadata']['page'] for doc in documents)) if documents else 0
       # Save the file after processing
       file_path = upload_dir / filename
       await file.seek(0)  # Correctly await the seek operation
       contents = await file.read()  # Read file contents
       # Write contents to file
       async with aiofiles.open(file_path, 'wb') as f:
           await f.write(contents)
       return JSONResponse(
           content={
               "message": "File uploaded and processed successfully",
               "filename": filename,
               "chunks": num_chunks,
               "pages": num_pages
           },
           status_code=200
       )
   except HTTPException as he:
       raise he
   except Exception as e:
       logger.error(f"Error in upload_file: {str(e)}")
       raise HTTPException(
           status_code=500,
           detail=f"Error processing file: {str(e)}"
       )
@router.post("/chat")
async def chat(
   question: str = Query(..., description="The question to ask about the documents"),
   model_type: str = Query("llama", description="Model type to use (llama or openai)"),
   temperature: float = Query(0.7, description="Temperature for response generation"),
   max_tokens: int = Query(1024, description="Maximum tokens to generate")
):
   try:
       # Get relevant chunks for the query
       relevant_chunks = await doc_processor.get_relevant_chunks(question)
      
       if not relevant_chunks:
           return JSONResponse(
               content={
                   "response": "No relevant information found in the uploaded documents. Please try another question or upload relevant documents.",
                   "sources": []
               },
               status_code=200
           )
       # Initialize LLM manager
       llm_manager = LLMManager(model_type)
       # Generate response
       response_text = llm_manager.get_response(  # Remove await here
           prompt=question,
           temperature=temperature,
           max_tokens=max_tokens,
           relevant_chunks=relevant_chunks
       )
       # Prepare source information
       sources = [
           {
               "source": chunk["metadata"]["source"],
               "page": chunk["metadata"]["page"],
               "score": chunk.get("score", 0)
           }
           for chunk in relevant_chunks
       ]
       return JSONResponse(
           content={
               "response": response_text,
               "sources": sources
           },
           status_code=200
       )
   except Exception as e:
       logger.error(f"Error in chat endpoint: {str(e)}")
       raise HTTPException(
           status_code=500,
           detail=f"Error generating response: {str(e)}"
       )
@router.get("/chat-history")
async def get_chat_history(model_type: str = "openai"):
    try:
        if model_type not in memory_managers:
            raise ModelNotFoundError(f"Unsupported model type: {model_type}")
        return memory_managers[model_type].get_chat_history()
    except ModelNotFoundError as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-history")
async def clear_history(model_type: str = "openai"):
    try:
        if model_type not in memory_managers:
            raise ModelNotFoundError(f"Unsupported model type: {model_type}")
        memory_managers[model_type].clear_memory()
        return {"message": "Chat history cleared successfully"}
    except ModelNotFoundError as e:
        raise e
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}


