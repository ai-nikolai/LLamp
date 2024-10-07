import openai
import time
import os

# from tenacity import (
#     retry,
#     stop_after_attempt, # type: ignore
#     wait_random_exponential, # type: ignore
# )

from llamp.llms.base_llm_system import BaseLLMSystem

class OpenAIChatTextSampling(BaseLLMSystem):
    def __init__(self, system_name="OpenAIChatTextSampling",save_path="game_logs", temperature=0.0, model="gpt-3.5-turbo-0125", stop_sequences=None, resample_temperature_jump=0.1):
        
        super().__init__(system_name, save_path, temperature=temperature)        
        self.client = openai.OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
        # api_key=OPENAI_KEY,
        )
        self.openai_attempts = 0
        self.model = model

        self.original_temperature = temperature

        self.current_sample = 0
        self.resample_temperature_jump = resample_temperature_jump

        self.previous_samples = {}
        self.resampling = False

        self.stop_sequences = stop_sequences
        self.__PREVIOUS_SAMPLES_KEY = "previous_samples"
        self.__DEFAULT_HISTORY_KEYS = ["role","content","temperature","out_token_action"]

    def act(self, current_observation="", temperature=None, return_token_count=False):
        """ Acting"""
        if not self.resampling:
            if not current_observation:
                raise Exception("You have to give an observation when you are not resampling.")
            self.temperature = self.original_temperature
            self.previous_samples = {}
            additional_logging_in = self._count_in_token(current_observation)
            self.add_to_history(current_observation, "user", additional_logging_in)

            in_tokens_count = self.count_tokens()
            assert additional_logging_in["in_token_all"]==in_tokens_count, "In Tokens need to be same length."


        action = self.call_model(temperature)
        additional_logging_out = self._count_out_token(action)

        action = self.post_process_model_output(action)

        if self.previous_samples:
            additional_logging = {}
            additional_logging.update(additional_logging_out)
            additional_logging.update(self.previous_samples)
        else:
            additional_logging = additional_logging_out

        self.add_to_history(action, "assistant", additional_data=additional_logging)

        self.resampling = False

        additional_logging_out.update(
            {
                "in_token_all" : self.full_history[-2]["in_token_all"],
                "in_token_message" : self.full_history[-2]["in_token_message"],
            }
        )
        if return_token_count:
            return action, additional_logging_out
        else:
            return action

    def prepare_resample(self, increase_temperature=True):
        """
        Stores the last interaction in another place and prepares for resample, including tracking of temperature.)
            
        Memory Structure:
        'user':,
        'content':,
        'temperature':,
        'previous_samples':[
            '0.0' : {'user':,'content':,'temperature':},
        ]
        """
        self.resampling = True
        previous_memory=self.pop_from_history(return_full=True)
        
        if not previous_memory:
            self.previous_samples = {}
            return

        else:
            previous_turn = {}
            for key in self.__DEFAULT_HISTORY_KEYS:
                previous_turn[key] = previous_memory[key]

            previous_samples = {}
            previous_samples_list = previous_memory.get(self.__PREVIOUS_SAMPLES_KEY)
            if not previous_samples_list:
                previous_samples_list = []
                

            previous_samples_list.append(previous_turn)
            previous_samples[self.__PREVIOUS_SAMPLES_KEY] = previous_samples_list

            self.previous_samples = previous_samples

        if increase_temperature:
            self.temperature += self.resample_temperature_jump


    def resample(self, increase_temperature=True):
        """ Samples again with increased temperature. """
        self.prepare_resample(increase_temperature)
        action = self.act()
        return action

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_model(self, temperature=None):
        """Call OpenAI API"""
        prompt = self.generate_text_prompt()

        full_prompt = [{
                "role": "user", 
                "content": prompt
        }]
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=full_prompt,
            temperature=self.temperature,
            stop = self.stop_sequences

        )
        chat_message = chat_completion.choices[0].message.content

        return chat_message

    def is_resample(self):
        """Returns whether this system is designed for resampling."""
        return True


if __name__=="__main__":
    agent = OpenAIChatTextSampling(save_path="./")
    prompt = []
    agent.set_base_prompt_and_reset(prompt)

    observation = "Hi"
    print("----")
    print("0")
    action = agent.act(observation)

    print(action)

    agent.save()
    agent.load_from_saved_data(agent.file_name)
    print("----")
    print("1")
    action = agent.act("Tell me a joke")
    print(action)
    agent.prepare_resample()
    print("----")
    print("2")
    action = agent.act("Tell me a joke2") #it will ignore the new utterance
    print(action)
    agent.prepare_resample(increase_temperature=False) 
    print("----")
    print("3")
    action = agent.act("") #utterance can be empty
    
    agent.prepare_resample() 
    print("----")
    print("4")
    action = agent.act("") #utterance can be empty

    print("----")
    print("5")
    action = agent.act("Something about airplanes would be funnier.") #utterance can be empty?
    print(action)

    agent.save()
    agent2 = OpenAIChatTextSampling(save_path="./",resample_temperature_jump=0.3)
    agent2.load_from_saved_data(agent.file_name)
    print("----")
    print("6")
    action = agent2.resample()
    print(action)
    agent2.save()


