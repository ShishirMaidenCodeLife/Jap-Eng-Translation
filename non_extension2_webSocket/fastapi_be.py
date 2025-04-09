# Backend Code (WebSocket Integration)
from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from googletrans import Translator

# Load OpenAI API Key
OPENAI_API_KEY = "openai key here"
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key. Please set it in a .env file.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin (you can limit this to your frontend URL for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = Translator()

@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")

            # Google Translate
            try:
                if request.text == "":
                    return {"openai": "", "googletrans": ""}
                google_translation = translator.translate(text, src='en', dest='ja').text
            except Exception as e:
                await websocket.send_json({"error": f"Google Translate failed: {str(e)}"})
                continue

            # OpenAI Translation
            openai_translation = ""
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                }
                data = {
                    "model": "gpt-4o-mini",  # Replace with your desired OpenAI model
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional language translator. Translate English to Japanese and Japanese to English without adding any extra content."
                        },
                        {
                            "role": "user",
                            "content": text,
                        },
                    ],
                }

                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                openai_translation = response.json()["choices"][0]["message"]["content"].strip()
                print("called OPENAI TRANSLATION: ", openai_translation)
            except requests.RequestException as e:
                await websocket.send_json({"error": f"OpenAI Translation failed: {str(e)}"})
                continue

            await websocket.send_json({
                "openai": openai_translation,
                "googletrans": google_translation,
            })
    except Exception as e:
        await websocket.close()
        print(f"WebSocket Connection Closed: {str(e)}")
