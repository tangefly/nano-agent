class Agent:

    def __init__(self, planner, skills):
        self.planner = planner
        self.skills = skills

    def run(self, query: str):

        print("start plan ...")
        plan = self.planner.plan(query)
        print("plan finished!")

        skill_name = plan["skill"]
        args = plan.get("args", {})

        if skill_name not in self.skills:
            return f"未知 skill: {skill_name}"

        return self.skills[skill_name].run(**args)
