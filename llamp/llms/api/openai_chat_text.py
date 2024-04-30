import openai
import time
import os

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

from llamp.llms.base_llm_system import BaseLLMSystem

class OpenAIChatText(BaseLLMSystem):
    def __init__(self, system_name="OpenAIChatText",save_path="game_logs", temperature=0.0, model="gpt-3.5-turbo-0125", stop_sequences=None):
        
        super().__init__(system_name, save_path, temperature=temperature)        
        self.client = openai.OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
        # api_key=OPENAI_KEY,
        )
        self.openai_attempts = 0

        self.model = model
        self.stop_sequences = stop_sequences


    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_model(self, temperature=None):
        """Call OpenAI API"""

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
    agent = OpenAITextChatAgent(save_path="./")
    prompt = []
    agent.save()

    agent.set_base_prompt_and_reset(prompt)


    observation = "Hi"
    action = agent.act(observation)

    print(action)

    agent.save()

    # EOF