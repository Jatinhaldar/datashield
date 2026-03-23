import os
import shutil
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shield import DataShield
from ai_client import get_ai_response, transcribe_audio
from database import log_interaction
from file_parser import extract_text_from_file

app = FastAPI(title="DataShield LLM Backend")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

shield = DataShield()

class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    original: str
    masked: str
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Masking
        masked_input = shield.mask_data(request.user_input)
        
        # 2. AI Response
        ai_response = await get_ai_response(masked_input)
        
        # 3. Log to Supabase (optional, runs if configured)
        log_interaction(
            original=request.user_input,
            masked=masked_input,
            response=ai_response
        )
        
        # 4. Return correct JSON structure
        return ChatResponse(
            original=request.user_input,
            masked=masked_input,
            response=ai_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=ChatResponse)
async def upload_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(default="Please analyze this uploaded document."),
    ocr_lang: str = Form(default="eng")
):
    try:
        # Read the uploaded file bytes
        file_bytes = await file.read()
        
        # 1. Extract text based on file type
        try:
            extracted_text = extract_text_from_file(file.filename, file_bytes, lang=ocr_lang)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in the file.")

        # 2. Masking the document content
        masked_document_text = shield.mask_data(extracted_text)
        
        # Combine the user prompt with the masked document content
        combined_final_input = f"User Prompt: {prompt}\n\nDocument Content:\n{masked_document_text}"
        
        # 3. AI Response
        ai_response = await get_ai_response(combined_final_input)
        
        # 4. Log to Supabase 
        # (We only log the first 500 chars to avoid database size limits on giant PDFs)
        log_interaction(
            original=f"[PROMPT: {prompt}] [FILE UPLOAD: {file.filename}] " + extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
            masked=f"[PROMPT: {prompt}] [FILE UPLOAD: {file.filename}] " + masked_document_text[:500] + ("..." if len(masked_document_text) > 500 else ""),
            response=ai_response
        )
        
        return ChatResponse(
            original=f"Prompt: {prompt}\nContext: {extracted_text}",
            masked=combined_final_input,
            response=ai_response
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice", response_model=ChatResponse)
async def voice_endpoint(file: UploadFile = File(...)):
    temp_file = NamedTemporaryFile(delete=False, suffix=f"_{file.filename}")
    try:
        # 1. Save uploaded audio to a temp file
        with open(temp_file.name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcribe using Groq Whisper
        transcription = await transcribe_audio(temp_file.name)
        if not transcription:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
        
        # 3. Masking
        masked_input = shield.mask_data(transcription)
        
        # 4. AI Response
        ai_response = await get_ai_response(masked_input)
        
        # 5. Log to Supabase
        log_interaction(
            original=f"[VOICE: {file.filename}] " + transcription,
            masked=masked_input,
            response=ai_response
        )
        
        return ChatResponse(
            original=transcription,
            masked=masked_input,
            response=ai_response
        )
        
    except Exception as e:
        print(f"Voice endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always cleanup temp file
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
