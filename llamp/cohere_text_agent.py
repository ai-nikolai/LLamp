import time
import os
import cohere

from .base_llm_agent import BaseLLMAgent

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

class CohereTextAgent(BaseLLMAgent):
    def __init__(self, agent_name="CohereTextAgent",save_path="game_logs", temperature = 0.0, model="command", stop_sequences=None):
        
        super().__init__(agent_name, save_path)
        self.base_prompt = [{
            "role" : "system",
            "content" : "You will interact with the environment to solve the given task. Think step by step "
        }]
        self.reset()
        API_KEY = os.environ['COHERE_API_KEY']
        self.co = cohere.Client(API_KEY)

        self.temperature = temperature
        self.model = model
        self.stop_sequences = stop_sequences

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6),reraise=True)
    def call_model(self):
        """Call OpenAI API"""

        prompt = self.generate_text_prompt()

        response = self.co.generate(
            model=self.model,
            prompt = prompt,
            temperature=self.temperature,
            end_sequences=self.stop_sequences #to have same behaviour as in Openai
            # stop_sequences=["}\n"] #included in text end_sequences if excluded
        )



        # print("="*20)
        # print(response)
        # print(type(response))
        # input(">")
        # print(response.generations[0].text)
        # input(">>")

        answer = response.generations[0].text

        return answer


if __name__=="__main__":
    print("Nothing to run here.")



 