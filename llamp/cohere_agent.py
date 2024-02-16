import openai
import time
import os
import cohere

from .base_llm_agent import BaseLLMAgent

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

class CohereAgent(BaseLLMAgent):
    def __init__(self, agent_name="CohereAgent",save_path="game_logs", temperature = 0.8):
        
        super().__init__(agent_name, save_path)
        self.base_prompt = [{
            "role" : "system",
            "content" : "You will interact with the environment to solve the given task. Think step by step "
        }]
        self.reset()
        API_KEY = os.environ['COHERE_API_KEY']
        self.co = cohere.Client(API_KEY)

        self.temperature = temperature
    
    def get_current_prompt_cohere(self):
        """Returns the current prompt and last message for Cohere's API"""
        out_list = []
        for messages in self.current_prompt:
            temp_dict = {}
            temp_dict["user_name"] = "Chatbot" if messages["role"] == "assistant" else "User"
            temp_dict["text"] = messages["content"]
            out_list.append(temp_dict)

        return out_list

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6),reraise=True)
    def call_model(self):
        """Call OpenAI API"""

        current_prompt = self.get_current_prompt_cohere()

        message = current_prompt[-1]["text"]
        if len(current_prompt)>1:
            chat_history = current_prompt[:-1]

        response = self.co.chat(
            message,
            model="command",
            chat_history=chat_history,
            temperature=self.temperature
            # stop_sequences=["}\n"]
        )

        answer = response.text
        return answer


if __name__=="__main__":
    print("Nothing to run here.")



 