import torch
import transformers

from .base_llm_agent import BaseLLMAgent

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

class MistralOrcaAgent(BaseLLMAgent):
	def __init__(self, agent_name="MistralOrcaAgent",save_path="game_logs", test_mode=False):

		super().__init__(agent_name, save_path)
		if torch.cuda.is_available():
			torch.set_default_device("cuda")
		else:
			torch.set_default_device("cpu")

		if test_mode:
			self.base_prompt=[
				{
					"content": "You are an assistant that answers one word.",
					"role": "system"
				}
			]
			self.reset()

		self.model = transformers.AutoModelForCausalLM.from_pretrained("Open-Orca/Mistral-7B-OpenOrca", device_map='auto', offload_folder="offload_mistral")

		# https://github.com/huggingface/transformers/issues/27132
		# please use the slow tokenizer since fast and slow tokenizer produces different tokens
		self.tokenizer = transformers.AutoTokenizer.from_pretrained(
			"microsoft/Orca-2-7b",
			use_fast=False,
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
	            "start" : "<|im_start|>assistant\n",
	            "end" : "<|im_end|>\n"
	        },
	        "user" : {
	            "start" : "<|im_start|>user\n",
	            "end" : "<|im_end|>\n"
	        },
	        "system" : {
	            "start" : "<|im_start|>system\n",
	            "end" : "<|im_end|>\n"
	        }        
	    }
	    prompt = ""
	    for message in self.current_prompt:
	        role = message["role"]
	        prompt += prompt_decorators[role]["start"]
	        prompt += message["content"]
	        prompt += prompt_decorators[role]["end"]

	    prompt += prompt_decorators["assistant"]["start"]

	    return prompt

	@staticmethod
	def extract_answer(output):
		"""Extracts the final answer from the Orca answer."""
		final_answer = output.split("assistant\n")[-1]
		final_answer = final_answer.replace("</s>","")
		return final_answer


	def call_model(self, attempt_limit = 100):
		"""Call OpenAI API"""
		
		prompt = self.construct_prompt_for_model()
		inputs = self.tokenizer(prompt, return_tensors='pt')
		output_ids = self.model.generate(inputs["input_ids"],)
		answer = self.tokenizer.batch_decode(output_ids)[0]

		final_answer = self.extract_answer(answer)

		return final_answer


if __name__=="__main__":
	print("Nothing to run here.")
