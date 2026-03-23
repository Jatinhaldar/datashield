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
                    "content": "You are a helpful assistant. Always provide your responses in a concise, point-wise (bulleted) format. Use bold headers for key sections."
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
        print(f"Error calling Groq Chat API: {e}")
        return "Sorry, I encountered an error while processing your request."

async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as file:
            transcription = await client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="text-verbose",
            )
            return transcription.text
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return ""
