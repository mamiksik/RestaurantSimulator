from environs import env
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

env.read_env()
client = OpenAI(api_key=env.str("OPENAI_KEY"))

def response_to_message(response: ChatCompletion) -> dict:
    return {
        "role": response.choices[0].message.role,
        "content": response.choices[0].message.content,
        "timestamp": response.created
    }


class ExtractedAnswers(BaseModel):
    dietary_preference: str
    top_3_favorite_foods: list[str]

class Chatbot:
    def __init__(self, *, model: str, system_prompt: str):
        self.model = model
        self.system_message = {"role": "system", "content": system_prompt}
        self.chat_history: list[dict] = []

    @property
    def latest_response(self) -> dict:
        if not self.chat_history:
            raise ValueError("No chat history available.")

        return self.chat_history[-1]

    def send_user_message(self, prompt: str) -> str:
        user_message = {"role": "user", "content": prompt}
        self.chat_history.append(user_message)
        return self.send_message(user_message)

    def send_message(self, message:dict=None) -> str:
        if message is not None:
            self.chat_history.append(message)

        response = client.chat.completions.create(
            model=self.model,
            messages=[self.system_message] + self.chat_history,
        )

        self.chat_history.append(response_to_message(response))
        return self.latest_response["content"]


    def __str__(self):
        return f"Chatbot(model={self.model}, system_prompt={self.system_message['content'][:50]}..., chat_history_length={len(self.chat_history)})"


