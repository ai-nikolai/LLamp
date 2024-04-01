import time
import os
import cohere

from .base_llm_agent import BaseLLMAgent

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

class CohereTextChatAgent(BaseLLMAgent):
    def __init__(self, agent_name="CohereTextChatAgent",save_path="game_logs", temperature = 0.0, model="command", stop_sequences=None):
        
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
    def call_model(self, temperature=None):
        """Call OpenAI API"""
        message = self.generate_text_prompt()

        response = self.co.chat(
            message = message,
            model=self.model,
            temperature=self.temperature,
            prompt_truncation = "AUTO_PRESERVE_ORDER",
            stop_sequences=self.stop_sequences
        )

        answer = response.text
        return answer


    # def post_process_model_output(self, model_output):
    #     """Manual shortening (as Cohere API doesn't allow for it yet)"""
    #     truncated_model_output = model_output.split(self.stop_sequences[0])[0]
    #     # Simple truncation for now.
    #     return truncated_model_output



if __name__=="__main__":
    print("Nothing to run here.")



 