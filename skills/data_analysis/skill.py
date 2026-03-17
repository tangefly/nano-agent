import pandas as pd
import re

def extract_code(text: str):
    # 提取 ```python ... ```
    pattern = r"```python(.*?)```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()

    # fallback：去掉 <think>
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    return text.strip()


class DataAnalysisSkill:

    def __init__(self, llm, python_tool):
        self.llm = llm
        self.python_tool = python_tool

    def run(self, query: str):

        file_path = "/data/sample.csv"

        # 构造 prompt
        prompt = open("skills/data_analysis/prompt.txt").read()

        prompt = prompt.format(query=query)

        code = self.llm.chat([
            {"role": "system", "content": prompt}
        ])

        code = extract_code(code)

        # 注入 df
        wrapped_code = f"""
{code}
"""

        result = self.python_tool.run(wrapped_code)

        return {
            "code": code,
            "result": result
        }