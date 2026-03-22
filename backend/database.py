import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def log_interaction(original: str, masked: str, response: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase credentials missing.")
        return None
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    data = {
        "original_input": original,
        "masked_input": masked,
        "ai_response": response
    }
    
    try:
        # Supabase REST API endpoint for table insertion
        endpoint = f"{SUPABASE_URL}/rest/v1/chat_logs"
        res = requests.post(endpoint, headers=headers, json=data)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"Error logging to Supabase via REST API: {e}")
        return None
