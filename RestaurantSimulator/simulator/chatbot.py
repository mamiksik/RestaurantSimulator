from environs import env
from openai import OpenAI, Omit
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

env.read_env()
client = OpenAI(api_key=env.str("OPENAI_KEY"))


class ExtractedAnswers(BaseModel):
    diet: str
    diet_usage: dict
    diet_model: str

    top3_dishes: list[str]
    top3_usage: dict
    top3_model: str

    @staticmethod
    def usage_to_dict(usage: CompletionUsage):
        return {
            "completion_tokens": usage.completion_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "total_tokens": usage.total_tokens,
        }


class StatefulChatbot:
    def __init__(self, *, model: str, system_prompt: str, temperature: float = Omit()):
        self.model = model
        self.temperature = temperature
        self.system_message = {"role": "system", "content": system_prompt}
        self.chat_history: list = []

    def send_user_message(self, prompt: str) -> ChatCompletion:
        user_message = {"role": "user", "content": prompt}
        return self.send_message(user_message)

    def send_message(self, message: dict = None) -> ChatCompletion:
        if message is not None:
            self.chat_history.append(message)

        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[self.system_message]
            + self.chat_history,  # This allows us to set system msg on existing thread
        )

        self.chat_history.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        return response

    def __str__(self):
        return f"Chatbot(model={self.model}, system_prompt={self.system_message['content'][:50]}..., chat_history_length={len(self.chat_history)})"
