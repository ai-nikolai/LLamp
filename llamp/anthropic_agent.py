import anthropic
# from anthropic import HUMAN_PROMPT, AI_PROMPT


import time
import os


from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

from .base_llm_agent import BaseLLMAgent

class AnthropicAgent(BaseLLMAgent):
	def __init__(self, agent_name="AntropicAgent",save_path="game_logs", temperature=0.0, model="claude-2.1", stop_sequences=None):
		
		super().__init__(agent_name, save_path)		
		self.client = anthropic.Anthropic(
		    # defaults to os.environ.get("ANTHROPIC_API_KEY")
		    # api_key="my_api_key",
		)
		# self.openai_attempts = 0

		self.temperature = temperature
		self.model = model
		self.stop_sequences = stop_sequences


	@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
	def call_model(self):
		"""Call OpenAI API"""
		message = self.client.messages.create(
		    model=self.model,
		    max_tokens=1000,
		    temperature=self.temperature,
		    system=self.current_prompt[0]["content"],
		    messages=self.current_prompt[1:],
		    stop_sequences=self.stop_sequences
		)
		
		response = message.content[0].text

		return response




if __name__=="__main__":
	print("Nothing to run here.")
	# def call_model(self, attempt_limit = 100):
	# 	"""Call OpenAI API"""
	# 	try:
	# 		print("Trying to call GPT")
	# 		chat_completion = self.client.chat.completions.create(
	# 		    # model="gpt-3.5-turbo",
	# 		    model="gpt-3.5-turbo-0125",
	# 		    # model="gpt-4-turbo-preview",
	# 		    messages=self.current_prompt,
	# 		    temperature=0.8
	# 		)
	# 		chat_message = chat_completion.choices[0].message.content
	# 		self.openai_attempts = 0
	# 	except openai.RateLimitError:
	# 		print(f"Need to wait ... attempt:{self.openai_attempts}")
	# 		time.sleep(20)
	# 		self.openai_attempts+=1
	# 		if self.openai_attempts < attempt_limit:
	# 			return self.call_model()
	# 		else:
	# 			raise Exception("Exceeded Attempt Limit")

	# 	return chat_message