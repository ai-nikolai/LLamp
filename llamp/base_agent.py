from datetime import datetime
import os
import json

class BaseAgent():
    LOG_FILE_ENDING = ".json"

    def __init__(self, agent_name="base",save_path="game_logs"):
        self.base_prompt = []
        self.current_prompt = []
        self.agent_name = agent_name
        self.save_path_base = save_path
        self.file_name = self.get_save_path()

    def call_model(self):
        """Not Implemented in base class."""
        raise NotImplementedError("call model needs to be implemented")


    def act(self, current_observation):
        """ Acting"""
        self.add_to_history(current_observation, "user")

        action = self.call_model()

        self.add_to_history(action, "assistant")

        return action

    def reset(self):
        """Resets the system (so far only the current_prompt)"""
        self.current_prompt = self.base_prompt
        self.file_name = self.get_save_path()

    def add_first_observation(self, first_obs):
        """ First Observation """
        self.add_to_history(first_obs, "user")

    def add_to_history(self, content, role):
        """ 
        Adds to the prompt.
        IF ERROR: This function used to be called  `add_to_prompt`
        """
        self.current_prompt.append({
            "role": role,
            "content": content
            })

    def pop_from_history(self):
        """Removes last element from history."""
        try:
            self.current_prompt.pop()
        except IndexError as e:
            pass

    def set_base_prompt_and_reset(self,base_prompt):
        """Sets a new base prompt and resets the agent."""
        self.base_prompt = base_prompt
        self.reset()

    
    def save(self):
        """Saves game interaction to file"""
        with open(self.file_name,"w") as file:
            json.dump(self.current_prompt,file,indent=4)

    def get_file_name(self, base_name="logs"):
        """creates a file name based on datetime"""
        now = datetime.now()
        file_name = self.agent_name+"_"+base_name+"_"+now.strftime("%d_%m_%Y_%H_%M_%S")+self.LOG_FILE_ENDING
        return file_name

    def get_save_path(self, save_path=""):
        """ Get Save path """
        if save_path:
            self.save_path_base = save_path
        self.create_save_path(self.save_path_base)
        file_name = os.path.join(self.save_path_base,self.get_file_name())
        return file_name

    def update_save_path(self,save_path):
        """ Update Save Path """
        self.save_path_base = save_path
        self.file_name = self.get_save_path(self.save_path_base)

    @staticmethod
    def create_save_path(save_path):
        """Creates the save path if it doesn't exist"""
        paths = os.path.split(save_path)
        current_path = ""
        for path in paths:
            if path: 
                current_path = os.path.join(current_path,path)
                if not os.path.exists(current_path):
                    os.mkdir(current_path)





    




if __name__=="__main__":
    print("Nothing to run here.")
