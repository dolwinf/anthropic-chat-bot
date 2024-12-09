from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from tool_config.tool_catalog import tools
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import anthropic
import os
import uvicorn
import re
from utils.tool_select import handle_tool_call

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


build_dir = Path(__file__).parent.parent / "client" / "build"


if not build_dir.exists() or not build_dir.is_dir():
    raise Exception(f"React build directory not found: {build_dir}")


app.mount("/static", StaticFiles(directory=str(build_dir / "static")), name="static")


@app.get("/")
@app.get("/{full_path:path}")
async def serve_app(full_path: str = ""):
    index_file = build_dir / "index.html"

    if full_path:
        static_file = build_dir / full_path
        if static_file.exists() and static_file.is_file() and not str(static_file).endswith('.html'):
            return FileResponse(static_file)

    if index_file.exists():
        return FileResponse(index_file)
    else:
        raise HTTPException(status_code=404, detail="index.html not found")


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
            system="You are a general bot answering questions. Use the appropriate tool if needed to call based on the reddit thread name mentioned by the user",
            tools=tools
        ) as stream:
            for text in stream.text_stream:
                response_content += text
                yield text

            final_response = stream.get_final_message()
            print(final_response)
            if final_response.stop_reason == "tool_use":
                tool_name = final_response.content[1].name
                for data in handle_tool_call(tool_name):
                    yield data

    return StreamingResponse(generate_response(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
