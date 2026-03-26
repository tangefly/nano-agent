from typing import Dict, Any, List, Optional
from .python_exec import SandboxExecTool
from manager import SessionManager
import traceback

import os

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、深圳"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位，默认为celsius"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "执行一段 bash 脚本",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "要执行的 bash 脚本"
                    }
                },
                "required": ["script"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "执行一段 python 代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 python 代码"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# 定义工具函数
def get_weather(location: str, unit: str = "celsius") -> str:
    """
    获取指定地点的天气信息
    """
    # 这里是模拟实现，实际应用中应该调用真实的天气API
    weather_data = {
        "北京": {"temperature": "25", "condition": "晴天"},
        "上海": {"temperature": "28", "condition": "多云"},
        "深圳": {"temperature": "30", "condition": "雷阵雨"},
    }
    
    if location in weather_data:
        data = weather_data[location]
        return f"{location}的天气：温度{data['temperature']}°{unit[0].upper()}, {data['condition']}"
    else:
        return f"未找到{location}的天气信息"

def run_bash(script: str, session_id: str):
    workdir = f"./tmp/agent_sandbox/{session_id}"
    os.makedirs(workdir, exist_ok=True)

    print(f"Working in {workdir} ...")

    # 临时文件名
    filename = "script.sh"
    file_path = os.path.join(workdir, filename)

    try:
        with open(file_path, "w") as f:
            f.write(script)
        os.chmod(file_path, 0o755)  # 给 bash 脚本加执行权限
    except Exception:
        return {
            "success": False,
            "error": "Failed to write file:\n" + traceback.format_exc()
        }
    
    return ["bash", filename]

def run_python(code: str, session_id: str):
    workdir = f"./tmp/agent_sandbox/{session_id}"
    os.makedirs(workdir, exist_ok=True)

    print(f"Working in {workdir} ...")

    # 临时文件名
    filename = "code.py"
    file_path = os.path.join(workdir, filename)

    try:
        with open(file_path, "w") as f:
            f.write(code)
    except Exception:
        return {
            "success": False,
            "error": "Failed to write file:\n" + traceback.format_exc()
        }

    return ["python", filename]

def run_bash_stream(script: str):
    exec_tool = SandboxExecTool()
    yield from exec_tool.run_bash_stream(script)

def run_python_stream(code: str):
    exec_tool = SandboxExecTool()
    yield from exec_tool.run_python_stream(code)


def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    执行工具调用
    """
    tool_map = {
        "get_weather": get_weather,
        "run_bash": run_bash,
        "run_python": run_python,
    }
    
    if tool_name in tool_map:
        try:
            result = tool_map[tool_name](**arguments)
            return result
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    else:
        return f"未知的工具：{tool_name}"

def execute_tool_call_stream(
    tool_name: str, 
    arguments: Dict[str, Any], 
    sessionManager: SessionManager, 
    session_id: str
):
    tool_map = {
        "run_bash": run_bash,
        "run_python": run_python,
    }

    print(f"tool_name: {tool_name}")

    if tool_name in tool_map:
        try:
            cmd_str = ""
            cmd = tool_map[tool_name](**arguments, session_id=session_id)
            for item in cmd:
                cmd_str += f"{item} "
            print(f"cmd: {cmd_str}")
            yield {
                "type": "tool_start",
                "cmd": cmd_str,
                "cwd": "/app"
            }
            yield from sessionManager.exec_stream(session_id, cmd)
        except Exception as e:
            print(f"error: {str(e)}")
            yield {
                "type": "error",
                "content": str(e)
            }
    else:
        yield {
            "type": "error",
            "content": f"未知工具: {tool_name}"
        }
