from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from googletrans import Translator

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

translator = Translator()


class TranslationRequest(BaseModel):
    q: str
    source: str
    target: str
    format: str


@app.post("/translate")
async def translate(request: TranslationRequest):
    translated = translator.translate(request.q,
                                      src=request.source,
                                      dest=request.target)

    if request.source == 'en' and request.target == 'ja':
        response_format = f"\nEn-->  " + request.q + "\nJa-->  " + translated.text
    elif request.source == 'ja' and request.target == 'en':
        response_format = f"\nJa-->  " + request.q + "\nEn-->  " + translated.text
    else:
        response_format = "Unsupported language pair."

    return {"translatedText": response_format}
