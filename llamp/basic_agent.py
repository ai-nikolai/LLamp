from datetime import datetime
import os
import json
import time

class BasicAgent():
	def __init__(self, agent_name="base",save_path="game_logs"):
		self.base_prompt=[
	    	{
		    	"role": "system", 
		   		"content": """You are a robot that is able to take decisions in an environment. 
		   		You responses should follow the syntax of the game, which consists of a command and an object (e.g. take book).
		   		This is the list of available commands together with a short description of each command. List:<<<
		   			look:                describe the current room
					goal:                print the goal of this game
					inventory:           print player's inventory
					go <dir>:            move the player north, east, south or west
					examine ...:         examine something more closely
					eat ...:             eat edible food
					open ...:            open a door or a container
					close ...:           close a door or a container
					drop ...:            drop an object on the floor
					take ...:            take an object that is on the floor
					put ... on ...:      place an object on a supporter
					take ... from ...:   take an object from a container or a supporter
					insert ... into ...: place an object into a container
					lock ... with ...:   lock a door or a container with a key
					unlock ... with ...: unlock a door or a container with a key >>> End of List.

		   		The `user` will be the actual game environement telling you about what you see and what you should do."""
	    	}
	    ]
		self.current_prompt = self.base_prompt
		self.agent_name = agent_name
		self.file_name = os.path.join(save_path,self.get_file_name())

	def get_file_name(self, base_name="logs"):
		"""creates a file name based on datetime"""
		now = datetime.now()
		file_name = self.agent_name+"_"+base_name+"_"+now.strftime("%d_%m_%Y_%H_%M_%S")
		return file_name

	def add_first_observation(self, first_obs):
		""" First Observation """
		self.add_to_prompt(first_obs, "user")

	def reset(self):
		"""Resets the system (so far only the current_prompt)"""
		self.current_prompt = self.base_prompt

	def add_to_prompt(self, content, role):
		""" Adds to the prompt."""
		self.current_prompt.append({
			"role": role,
			"content": content
			})

	def act(self, current_observation):
		""" Acting"""
		self.add_to_prompt(current_observation, "user")

		action = self.call_model()

		self.add_to_prompt(action, "assistant")

		return action

	def save(self):
		"""Saves game interaction to file"""
		with open(self.file_name,"w") as file:
			json.dump(self.current_prompt,file,indent=4)

	def call_model(self):
		"""Not Implemented in base class."""
		raise NotImplementedError("call model needs to be implemented")



	




if __name__=="__main__":
	print("Nothing to run here.")
