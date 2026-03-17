import json

class Planner:

    def __init__(self, llm):
        self.llm = llm

    def plan(self, query: str):
        prompt = f"""
你是一个Agent规划器，请决定使用哪个skill。

可用skills:
- data_analysis: 用于分析CSV数据

返回JSON：
{{
  "skill": "...",
  "args": {{...}}
}}

用户请求:
{query}
"""

        output = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        try:
            return json.loads(output)
        except:
            return {"skill": "data_analysis", "args": {"query": query}}
