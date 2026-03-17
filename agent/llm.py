from openai import OpenAI

class LLM:

    def __init__(self, model, base_url):
        self.client = OpenAI(
            base_url=base_url,
            api_key="EMPTY"  # vLLM 不需要真实 key
        )
        self.model = model

    def chat(self, messages):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )
        return resp.choices[0].message.content
