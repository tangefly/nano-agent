from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
import json
from tools.functions import tools, execute_tool_call, execute_tool_call_stream
from typing import Dict, Any, List, Optional
import uuid

from manager.session_manager import SessionManager


app = FastAPI()

# model = "deepseek-chat"
# api_key = "sk-2c1acc209f964b989506be2f1b1a8d15"
# base_url = "https://api.deepseek.com"

model = "Qwen3-14B-FP8"
api_key = "sk-2c1acc209f964b989506be2f1b1a8d15"
base_url = "http://127.0.0.1:8000/v1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

async def process_stream_with_tools(
    messages: List[Dict],
    max_iterations: int = 10
):

    sessionManager = SessionManager()

    iteration = 0
    session_id = None

    while iteration < max_iterations:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            stream=True
        )
        
        tool_calls_accumulated: Dict[int, Dict] = {}
        current_content = ""
        
        for chunk in stream:
            delta = chunk.choices[0].delta
            
            if delta.content:
                current_content += delta.content

                yield f"data: {json.dumps({
                    'type': 'chat',
                    'content': delta.content
                }, ensure_ascii=False)}\n\n"
            
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    index = tool_call.index
                    
                    if index not in tool_calls_accumulated:
                        tool_calls_accumulated[index] = {
                            'id': tool_call.id,
                            'type': tool_call.type,
                            'function': {
                                'name': tool_call.function.name or '',
                                'arguments': tool_call.function.arguments or ''
                            }
                        }
                    else:
                        if tool_call.function.arguments:
                            tool_calls_accumulated[index]['function']['arguments'] += tool_call.function.arguments
                        if tool_call.function.name:
                            tool_calls_accumulated[index]['function']['name'] = tool_call.function.name
                        if tool_call.id:
                            tool_calls_accumulated[index]['id'] = tool_call.id
        
        if tool_calls_accumulated:
            print("tool call")
            
            messages.append({
                "role": "assistant",
                "content": current_content or None,
                "tool_calls": list(tool_calls_accumulated.values())
            })
            
            for index, tool_call in sorted(tool_calls_accumulated.items()):
                tool_name = tool_call['function']['name']
                arguments_str = tool_call['function']['arguments']
                
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError:
                    arguments = {}

                tool_output = ""

                if session_id is None:
                    session_id = sessionManager.create_session()

                for item in execute_tool_call_stream(tool_name, arguments, sessionManager, session_id):
                    if item["type"] == "tool_stdout":
                        yield f"data: {json.dumps({
                            'type': 'terminal',
                            'content': item['content']
                        }, ensure_ascii=False)}\n\n"

                        tool_output += item["content"]

                    elif item["type"] == "step":
                        yield f"data: {json.dumps({
                            'type': 'status',
                            'content': item['content']
                        }, ensure_ascii=False)}\n\n"

                    elif item["type"] == "tool_start":
                         yield f"data: {json.dumps({
                            'type': 'tool_start',
                            "cmd": item['cmd'],
                            "cwd": item['cwd']
                        }, ensure_ascii=False)}\n\n"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": tool_output or "done"
                })

                print(f"{tool_output}")
            
            iteration += 1
        else:
            break

@app.post("/chat")
async def chat(req: dict):
    messages = req["messages"]

    async def generator():
        async for data in process_stream_with_tools(messages):
            yield data
    
    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )