from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic
import os

app = FastAPI()
client = anthropic.Anthropic(api_key=os.getenv("SONNET_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str
    conversation_id: str


@app.post("/chat")
def chat_endpoint(query: ChatMessage):

    def generate_response():
        response_content = ""
        with client.messages.stream(
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": query.message
            }],
            model="claude-3-5-sonnet-20241022",
        ) as stream:
            for text in stream.text_stream:
                response_content += text
                yield text

    return StreamingResponse(generate_response(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)