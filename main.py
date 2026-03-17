from agent.core import Agent
from agent.planner import Planner
from agent.llm import LLM

from tools.python_exec import PythonExecTool
from skills.data_analysis.skill import DataAnalysisSkill

llm = LLM(model="Qwen3-4B", base_url="http://localhost:8000/v1")

planner = Planner(llm)

python_tool = PythonExecTool()

skills = {
    "data_analysis": DataAnalysisSkill(llm, python_tool)
}

agent = Agent(planner, skills)

print("start analysis user's query ...")

prompt = """
我的数据格式如下：

name,score
Alice,20
Bob,50
Charlie,10
David,20

分析 /data/sample.csv，画出一个饼图，展示每个人的分数占比，并保存到 /data 目录下面
"""

result = agent.run(prompt)

print(result)
