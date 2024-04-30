from datetime import datetime
import os
import json

from llamp.base_agent import BaseAgent


class BaseLLMAgent(BaseAgent):
	def __init__(self, agent_name="base_llm",save_path="game_logs", temperature=0):
		super().__init__(agent_name, save_path)
		self.base_prompt=[]
		self.current_prompt = self.base_prompt
		self.agent_name = agent_name
		self.file_name = self.get_save_path(save_path)
		self.temperature=temperature
	
	def _extend_memory(self, memory):
		""" Helper function to extend memory"""
		memory.update({"temperature":self.temperature})
		return memory

	def act(self, current_observation, temperature=None):
		""" Acting"""
		self.add_to_history(current_observation, "user")

		action = self.call_model(temperature)

		action = self.post_process_model_output(action)

		self.add_to_history(action, "assistant")

		return action

	def call_model(self, temperature=None):
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
	    
