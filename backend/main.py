from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shield import DataShield
from ai_client import get_ai_response
from database import log_interaction

app = FastAPI(title="DataShield LLM Backend")

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
