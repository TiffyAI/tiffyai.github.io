import os
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("Missing OpenAI API key in environment")
openai.api_key = OPENAI_API_KEY

app = FastAPI()

class AskRequest(BaseModel):
    messages: list

@app.post("/ask")
async def ask(request: AskRequest):
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=request.messages,
            temperature=0.7
        )
        return {"choices": resp.choices}
    except Exception as e:
        logging.error("OpenAI request failed: %s", e)
        return {"error": str(e)}

@app.get("/healthcheck")
def health():
    return {"status": "OK"}
