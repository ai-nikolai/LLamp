# import openai
import time
import os

from cerebras.cloud.sdk import Cerebras



# from tenacity import (
#     retry,
#     stop_after_attempt, # type: ignore
#     wait_random_exponential, # type: ignore
# )

from llamp.llms.base_llm_system import BaseLLMSystem

class CerebrasChatText(BaseLLMSystem):
    def __init__(self, system_name="CerebrasChatText",save_path="game_logs", temperature=0.0, model="llama3.1-8b", stop_sequences=None):
        
        super().__init__(system_name, save_path, temperature=temperature)    
        self.client  = Cerebras(
            # This is the default and can be omitted
            api_key=os.environ.get("CEREBRAS_API_KEY"),
        )    
        # self.client = openai.OpenAI(
        #   base_url = "https://api.cerebras.ai/v1/chat/completions",
        #   api_key = os.environ.get("CEREBRAS_API_KEY")
        # )
        self.openai_attempts = 0

        self.model = model
        self.stop_sequences = stop_sequences


    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_model(self, temperature=None):
        """Call CEREBRAS API"""

        prompt = self.generate_text_prompt()

        full_prompt = [{
                "role": "user", 
                "content": prompt
        }]

        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=full_prompt,
            temperature=self.temperature,
            stop = self.stop_sequences

        )
        chat_message = chat_completion.choices[0].message.content

        return chat_message


if __name__=="__main__":
    print("Nothing to run here.")
    agent = CerebrasChatText(save_path="./")
    prompt = []
    agent.save()

    agent.set_base_prompt_and_reset(prompt)


    observation = "Hi"
    action = agent.act(observation)

    print(action)

    agent.save()

    # EOF