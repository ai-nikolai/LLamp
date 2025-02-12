import time
import os

# from tenacity import (
#     retry,
#     stop_after_attempt, # type: ignore
#     wait_random_exponential, # type: ignore
# )
import google.generativeai as genai


from llamp.llms.base_llm_system import BaseLLMSystem

class GoogleChatText(BaseLLMSystem):
    def __init__(self, system_name="GoogleChatText",save_path="game_logs", temperature=0.0, model="gemini-1.5-flash-002", stop_sequences=None):
        
        super().__init__(system_name, save_path, temperature=temperature) 
        genai.configure(api_key=os.environ["GOOGLE_AI_API_KEY"])
        self.online_model = genai.GenerativeModel(model)
        self.openai_attempts = 0

        self.model = model
        self.stop_sequences = stop_sequences


    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_model(self, temperature=None):
        """Call OpenAI API"""
        prompt = self.generate_text_prompt()

        generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                stop_sequences=self.stop_sequences,
                max_output_tokens=8000,
                temperature=temperature,
        )

        response = self.online_model.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.text



if __name__=="__main__":
    agent = GoogleChatText(save_path="./")
    prompt = []
    agent.set_base_prompt_and_reset(prompt)
    observation = "Hi"
    action = agent.act(observation)
    print(action)

    # agent.save()
    # EOF