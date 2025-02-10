from datetime import datetime
import os
import json

import tiktoken

from llamp.llms.base_system import BaseSystem


class BaseLLMSystem(BaseSystem):
	def __init__(self, system_name="base_llm",save_path="game_logs", temperature=0):
		super().__init__(system_name, save_path)
		self.base_prompt=[]
		self.current_prompt = self.base_prompt
		self.system_name = system_name
		self.file_name = self.get_save_path(save_path)
		self.temperature=temperature
	
	def _extend_memory(self, memory):
		""" Helper function to extend memory"""
		memory.update({"temperature":self.temperature})
		return memory

	def _count_in_token(self, current_observation):
		""" counts in tokens based on current_observation. """
		tokens_until_now = self.count_tokens()
		current_message_tokens = self.count_tokens(current_observation)
		in_tokens = tokens_until_now+current_message_tokens
		
		additional_logging = {
			"in_token_all": in_tokens,
			"in_token_message" : current_message_tokens
		}

		return additional_logging

	def _count_out_token(self, action):
		""" Counts out token based on action. """
		out_token = self.count_tokens(action)
		new_additional_logging = {
			"out_token_action":out_token		
		}

		return new_additional_logging

	def act(self, current_observation, temperature=None, return_token_count=False):
		""" Acting"""
		additional_logging_in = self._count_in_token(current_observation)
		self.add_to_history(current_observation, "user", additional_logging_in)
		
		in_tokens_count = self.count_tokens()
		if not (additional_logging_in["in_token_all"]==in_tokens_count):
			print("WARNING: In Tokens need to be same length.")
			print(f"additional_logging_in={additional_logging_in['in_token_all']}")
			print(f"in_tokens_count={in_tokens_count}")

		action = self.call_model(temperature)
		additional_logging_out = self._count_out_token(action)

		action = self.post_process_model_output(action)
		self.add_to_history(action, "assistant", additional_logging_out)

		additional_logging = {}
		additional_logging.update(additional_logging_in)
		additional_logging.update(additional_logging_out)
		if return_token_count:
			return action, additional_logging
		else:
			return action

	def call_model(self, temperature=None, return_token_count=False):
		"""Not Implemented in base class."""
		raise NotImplementedError("call model needs to be implemented")

	def post_process_model_output(self,model_output):
		"""Some post processing"""
		return model_output
   	
	def generate_text_prompt(self):
		"""Generates a text prompt for the 'old school' LLMs."""
		prompt = ""
		for section in self.current_prompt:
			prompt +=  section["content"]
		# prompt+="\n"
		return prompt

	def count_tokens(self, optional_text=None, model_name="gpt-3.5"):
		"""
		By default we are returning the openai tokenizer count. 
		If a model wants a better tokenizer it needs to provide its own.
		"""
		model_name_clean = "-".join(model_name.split("-")[:2])
		encoding = tiktoken.encoding_for_model(model_name_clean)
		if optional_text:
			token_count = len(encoding.encode(optional_text))
		else:
			prompt = self.generate_text_prompt()
			token_count = len(encoding.encode(prompt))

		return token_count


if __name__=="__main__":
	agent = BaseLLMAgent()
	print("Nothing to run here.")
	agent.add_to_history("hi","user")
	agent.add_to_history("do this","assistant")
	print(agent.generate_text_prompt())




# 
# 	    	{
# 		    	"role": "system", 
# 		   		"content": 
# """
# You are a robot that is able to take decisions in an interactive environment. 
# The `user` will be the actual game environment telling you about what your observations from the environment.

# Your responses should follow the syntax of the game. 
# You should respond with one command at every interaction only. 
# Each command should be a single command from the list of valid commands. 
# This is the list of available and valid commands together with a short description of each command.
# <<<
# look:                describe the current room
# goal:                print the goal of this game
# inventory:           print player's inventory
# go <dir>:            move the player north, east, south or west
# examine ...:         examine something more closely
# eat ...:             eat edible food
# open ...:            open a door or a container
# close ...:           close a door or a container
# drop ...:            drop an object on the floor
# take ...:            take an object that is on the floor
# put ... in/on ...:      place an object on a supporter
# take ... from ...:   take an object from a container or a supporter
# insert ... into ...: place an object into a container
# lock ... with ...:   lock a door or a container with a key
# unlock ... with ...: unlock a door or a container with a key 
# >>>
# """
# 	    	}
	    
