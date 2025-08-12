import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# Get API key & Assistant ID from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

if not OPENAI_API_KEY or not ASSISTANT_ID:
    raise ValueError("OPENAI_API_KEY or OPENAI_ASSISTANT_ID not set in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# Allow Blogspot & GitHub Pages to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your Blogspot domain later for security
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()

    if not question:
        return {"error": "No question provided."}

    # Create a new conversation thread
    thread = client.beta.threads.create()

    # Add the user question
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # Wait until it's done
    while True:
        status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if status.status == "completed":
            break
        time.sleep(1)

    # Get the latest reply
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value

    return {"answer": answer}
