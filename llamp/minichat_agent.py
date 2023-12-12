import torch
import transformers

from .base_llm_agent import BaseLLMAgent

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

class MiniChatAgent(BaseLLMAgent):
	def __init__(self, agent_name="MiniChatAgent",save_path="game_logs", test_mode=False):

		super().__init__(agent_name, save_path)
		if torch.cuda.is_available():
			torch.set_default_device("cuda")
		elif torch.backends.mps.is_available():
			self.mps_device = torch.device("mps") 
		else:
			torch.set_default_device("cpu")

		if test_mode:
			self.base_prompt=[
				{
					"content": "Answer one word.",
					"role": "system"
				}
			]
			self.reset()

		self.model = transformers.AutoModelForCausalLM.from_pretrained("GeneZC/MiniChat-3B", device_map='auto', use_cache=True, torch_dtype=torch.float16)

		if self.mps_device:
			self.model.to(self.mps_device)

		# https://github.com/huggingface/transformers/issues/27132
		# please use the slow tokenizer since fast and slow tokenizer produces different tokens
		self.tokenizer = transformers.AutoTokenizer.from_pretrained(
			"GeneZC/MiniChat-3B",
		)		

	def construct_prompt_for_model(self):
	    """
	    Constructs a prompt for the ORCA 2 model using the OpenAI structure of `messages`
	    I.e. messages = [
	        {
	            "content" : "Bla bla bla",
	            "role": "assistant / user / system"
	        }
	    ]
	    """
	    prompt_decorators ={
	        "assistant" : {
	            "start" : "[|Assistant|]",
	            "end" : ""
	        },
	        "user" : {
	            "start" : "<s>[|User|]",
	            "end" : "</s>"
	        },
	        "system" : {
	            "start" : "<s>[|System|]",
	            "end" : ""
	        },
	        "user_sys" : {
	            "start" : "[|User|]",
	            "end" : "</s>"
	        }	              
	    }
	    role_is_sys=False
	    prompt = ""
	    for message in self.current_prompt:
	        role = message["role"]
	        if role == "system":
	        	role_is_sys=True

	        if role_is_sys & (role=="user"):
	        	role="user_sys"

	        if role_is_sys & (role=="assistant"):
	        	role_is_sys=False

	        prompt += prompt_decorators[role]["start"]
	        prompt += message["content"]
	        prompt += prompt_decorators[role]["end"]

	    prompt += prompt_decorators["assistant"]["start"]

	    return prompt

	@staticmethod
	def extract_answer(output):
		"""Extracts the final answer from the Orca answer."""
		final_answer = output.split("[|Assistant|]")[-1]
		return final_answer


	def call_model(self, attempt_limit = 100):
		"""Call OpenAI API"""
		
		prompt = self.construct_prompt_for_model()
		inputs = self.tokenizer(prompt, return_tensors='pt')
		if self.mps_device:
			inputs.to(self.mps_device)
		output_ids = self.model.generate(inputs["input_ids"],)
		answer = self.tokenizer.batch_decode(output_ids)[0]

		final_answer = self.extract_answer(answer)

		return final_answer


if __name__=="__main__":
	print("Nothing to run here.")
