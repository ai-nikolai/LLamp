import openai
import time
import os

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

from llamp.llms.base_llm_system import BaseLLMSystem

class OpenAIText(BaseLLMSystem):
    def __init__(self, system_name="OpenAIText",save_path="game_logs", temperature=0.0, model="davinci-002", stop_sequences=None):
        
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
        # print("=+"*20)
        # print(prompt)
        # input(">")

        completion = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            stop=self.stop_sequences,
            max_tokens=250
        )
        message = completion.choices[0].text
        # print("-+"*20)
        # print(message)
        # print(completion.usage)
        # print("-+"*20)

        return message




if __name__=="__main__":
    print("Nothing to run here.")
    # def call_model(self, attempt_limit = 100):
    #   """Call OpenAI API"""
    #   try:
    #       print("Trying to call GPT")
    #       chat_completion = self.client.chat.completions.create(
    #           # model="gpt-3.5-turbo",
    #           model="gpt-3.5-turbo-0125",
    #           # model="gpt-4-turbo-preview",
    #           messages=self.current_prompt,
    #           temperature=0.8
    #       )
    #       chat_message = chat_completion.choices[0].message.content
    #       self.openai_attempts = 0
    #   except openai.RateLimitError:
    #       print(f"Need to wait ... attempt:{self.openai_attempts}")
    #       time.sleep(20)
    #       self.openai_attempts+=1
    #       if self.openai_attempts < attempt_limit:
    #           return self.call_model()
    #       else:
    #           raise Exception("Exceeded Attempt Limit")

    #   return chat_message