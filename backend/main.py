from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import json
from groq import Groq

app = FastAPI()

# Allow React to talk to Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq (Replace with your key)
client = Groq(api_key="YOUR_GROQ_API_KEY")

def split_chapters(text):
    # Regex to find chapters (Chapter 1, Prologue, etc.)
    chapters = re.split(r'(?i)(?=chapter|part|prologue)', text)
    return [c.strip() for c in chapters if len(c.strip()) > 100]

@app.post("/analyze")
async def analyze_book(file: UploadFile = File(...)):
    try:
        content = (await file.read()).decode("utf-8")
        word_count = len(content.split())
        read_time = round(word_count / 238) # Standard WPM
        
        chapters = split_chapters(content)
        sample_text = content[:15000] # Analyze the start for metadata

        prompt = (
            "You are an Elite Literary Critic. Analyze this text and return ONLY a JSON object: "
            "{"
            "'genre': 'string', 'profanity_level': 'string', 'novel_type': 'string', "
            "'vocab_level': 'Beginner/Intermediate/Advanced', "
            "'summaries': {"
                "'plot': 'Short executive plot summary', "
                "'thematic': 'Deep dive into philosophical themes', "
                "'emotional': 'The vibe and emotional journey'"
            "},"
            "'sentiment_emoji': 'one emoji'"
            "}"
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{prompt}\n\nText: {sample_text}"}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(chat_completion.choices[0].message.content)
        
        return {
            "metadata": {
                "word_count": word_count,
                "read_time": read_time,
                "chapter_count": len(chapters)
            },
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)