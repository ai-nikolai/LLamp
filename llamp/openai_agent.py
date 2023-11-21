import openai
from .basic_agent import BasicAgent

class OpenAIAgent(BasicAgent):
	def __init__(self, agent_name="OpenAIAgent",save_path="game_logs"):
		
		super().__init__(agent_name, save_path)		
		self.client = openai.OpenAI(
	    # Defaults to os.environ.get("OPENAI_API_KEY")
	    # api_key=OPENAI_KEY,
		)
		self.openai_attempts = 0

	def call_model(self, attempt_limit = 100):
		"""Call OpenAI API"""
		try:
			print("Trying to call GPT")
			chat_completion = self.client.chat.completions.create(
			    model="gpt-3.5-turbo",
			    messages=self.current_prompt
			)
			chat_message = chat_completion.choices[0].message.content
			self.openai_attempts = 0
		except openai.RateLimitError:
			print(f"Need to wait ... attempt:{self.openai_attempts}")
			time.sleep(20)
			self.openai_attempts+=1
			if self.openai_attempts < attempt_limit:
				return self.call_gpt()
			else:
				raise Exception("Exceeded Attempt Limit")

		return chat_message


if __name__=="__main__":
	print("Nothing to run here.")
