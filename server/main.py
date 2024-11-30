from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from tool_config.tool_catalog import tools
from tools.reddit import get_bard_reddit_threads
import anthropic
import os
import uvicorn

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
            system="You are a general bot answering questions. Use the tools only if indiciation of words like Bard and reddit",
            tools=tools
        ) as stream:
            for text in stream.text_stream:
                response_content += text
                yield text

            final_response = stream.get_final_message()
            print(final_response)
            if final_response.stop_reason == "tool_use":
                for data in get_bard_reddit_threads():
                    yield data

    return StreamingResponse(generate_response(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
