from datetime import datetime
import os
import json
from copy import deepcopy


class AnyDict:
    def __init__(self, value=-1):
        self.value = value

    def __getitem__(self,key):
        return self.value

class BaseSystem():
    LOG_FILE_ENDING = ".json"

    def __init__(self, system_name="base",save_path="game_logs", *args, **kwargs):
        self.base_prompt = []
        self.current_prompt = []
        self.full_history = []
        self.system_name = system_name
        self.save_path_base = save_path
        self.file_name = self.get_save_path()

    def call_model(self):
        """Not Implemented in base class."""
        raise NotImplementedError("call model needs to be implemented")


    def act(self, current_observation, return_token_count=False, *args, **kwargs):
        """ Acting"""
        self.add_to_history(current_observation, "user")

        action = self.call_model()

        self.add_to_history(action, "assistant")

        if return_token_count:
            return action, AnyDict()
        else:
            return action

    def reset(self, *args, **kwargs):
        """Resets the system (so far only the current_prompt)"""
        self.current_prompt = deepcopy(self.base_prompt)
        self.full_history = deepcopy(self.current_prompt)
        self.file_name = self.get_save_path()


    def _extend_memory(self, memory, *args, **kwargs):
        """Extends memory. Change for specific classes to record more data"""
        return memory

    def add_first_observation(self, first_obs, *args, **kwargs):
        """ First Observation """
        self.add_to_history(first_obs, "user")

    def add_to_history(self, content, role, additional_data={}, *args, **kwargs):
        """ 
        Adds to the prompt.
        IF ERROR: This function used to be called  `add_to_prompt`
        """
        tmp = {
            "role": role,
            "content": content
            }

        self.current_prompt.append(tmp)

        tmp.update(additional_data)
        
        # To log additional data by default
        tmp = self._extend_memory(tmp)
        self.full_history.append(tmp)


    def pop_from_history(self, return_full=True, *args, **kwargs):
        """Removes last element from history."""
        try:
            if return_full:
                self.current_prompt.pop()
                return self.full_history.pop()
            else:
                self.full_history.pop()
                return self.current_prompt.pop() 
        except IndexError as e:
            pass


    def update_latest_history(self, content, key="content", old_key="old_content", *args, **kwargs):
        """
        Updates the latest history with new content. By default uses the key 'content' 
        """
        previous_content = self.full_history[-1][key]
        self.full_history[-1][key] = content
        self.full_history[-1][old_key] = previous_content


    def _extract_prompt_from_history(self, history, keys_to_keep_in_prompt=["role","content"], *args, **kwargs):
        """Extracts prompt from history."""
        prompt = []
        for segment in history:
            tmp = {}
            for key in keys_to_keep_in_prompt:
                tmp[key] = segment.get(key)

            prompt.append(tmp)
        return prompt

    def load_from_saved_data(self, previous_history, keys_to_keep_in_prompt=["role","content"], *args, **kwargs):
        """
        Loads the saved prompt
        Input Options:
        - Previous History as list
        - Previous Histroy as FileName
        - Previous History as FilePointer
        """
        self.reset()
        
        import io
        if type(previous_history)==list:
            self.full_history = previous_history

        elif type(previous_history)==str:
            import json
            with open(previous_history) as file:
                previous_history = json.load(file)
            self.full_history = previous_history

        elif type(previous_history)==io.TextIOWrapper:
            previous_history = json.load(previous_history)
            self.full_history = previous_history

        self.current_prompt = self._extract_prompt_from_history(self.full_history, keys_to_keep_in_prompt)


    def set_base_prompt_and_reset(self,base_prompt, *args, **kwargs):
        """Sets a new base prompt and resets the agent."""
        self.base_prompt = base_prompt
        self.reset()

    
    def save(self, *args, **kwargs):
        """Saves game interaction to file"""
        with open(self.file_name,"w") as file:
            json.dump(self.full_history,file,indent=4)

    def get_file_name(self, base_name="logs", *args, **kwargs):
        """creates a file name based on datetime"""
        now = datetime.now()
        file_name = self.system_name+"_"+base_name+"_"+now.strftime("%d_%m_%Y_%H_%M_%S")+self.LOG_FILE_ENDING
        return file_name

    def get_save_path(self, save_path="", *args, **kwargs):
        """ Get Save path """
        if save_path:
            self.save_path_base = save_path
        self.create_save_path(self.save_path_base)
        file_name = os.path.join(self.save_path_base,self.get_file_name())
        return file_name

    def update_save_path(self,save_path, *args, **kwargs):
        """ Update Save Path """
        self.save_path_base = save_path
        self.file_name = self.get_save_path(self.save_path_base)

    @staticmethod
    def create_save_path(save_path, *args, **kwargs):
        """Creates the save path if it doesn't exist"""
        paths = os.path.split(save_path)
        current_path = ""
        for path in paths:
            if path: 
                current_path = os.path.join(current_path,path)
                if not os.path.exists(current_path):
                    os.mkdir(current_path)


    def count_tokens(self, *args, **kwargs):
        """ Creating this function for completeness """
        return 0

    def is_resample(self, *args, **kwargs):
        """Returns whether this system is designed for resampling."""
        return False
    




if __name__=="__main__":
    print("Nothing to run here.")
