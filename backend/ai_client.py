import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

# Initialize the Groq client
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def get_ai_response(prompt: str) -> str:
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant", # Updated model since the older one was decommissioned
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "Sorry, I encountered an error while processing your request."
