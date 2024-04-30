import openai
import time
import os

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

from llamp.base_llm_agent import BaseLLMAgent

class OpenAITextChatSamplingAgent(BaseLLMAgent):
    def __init__(self, agent_name="OpenAITextChatSamplingAgent",save_path="game_logs", temperature=0.0, model="gpt-3.5-turbo-0125", stop_sequences=None, temperature_jump=0.2):
        
        super().__init__(agent_name, save_path, temperature=temperature)        
        self.client = openai.OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
        # api_key=OPENAI_KEY,
        )
        self.openai_attempts = 0
        self.model = model

        self.original_temperature = temperature

        self.current_sample = 0
        self.temperature_jump = temperature_jump

        self.previous_samples = {}
        self.resampling = False

        self.stop_sequences = stop_sequences
        self.__PREVIOUS_SAMPLES_KEY = "previous_samples"
        self.__DEFAULT_PROMPT_KEYS = ["role","content"]


    def act(self, current_observation="", temperature=None):
        """ Acting"""
        if not self.resampling:
            if not current_observation:
                raise Exception("You have to give an observation when you are not resampling.")
            self.temperature = self.original_temperature
            self.previous_samples = {}
            self.add_to_history(current_observation, "user")

        action = self.call_model(temperature)

        action = self.post_process_model_output(action)

        self.add_to_history(action, "assistant", additional_data=self.previous_samples)

        self.resampling = False

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
            for key in self.__DEFAULT_PROMPT_KEYS:
                previous_turn[key] = previous_memory[key]
            previous_turn["temperature"] = self.temperature

            previous_samples = {}
            previous_samples_list = previous_memory.get(self.__PREVIOUS_SAMPLES_KEY)
            if not previous_samples_list:
                previous_samples_list = []
                

            previous_samples_list.append(previous_turn)
            previous_samples[self.__PREVIOUS_SAMPLES_KEY] = previous_samples_list

            self.previous_samples = previous_samples

        if increase_temperature:
            self.temperature += self.temperature_jump


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


if __name__=="__main__":
    agent = OpenAITextChatSamplingAgent(save_path="./")
    prompt = []
    agent.set_base_prompt_and_reset(prompt)

    observation = "Hi"
    action = agent.act(observation)

    print(action)

    agent.save()
    agent.load_from_saved_data(agent.file_name)
    action = agent.act("Tell me a joke")
    print(action)
    agent.prepare_resample()
    action = agent.act("Tell me a joke2") #it will ignore the new utterance
    print(action)
    agent.prepare_resample(increase_temperature=False) 
    action = agent.act("") #utterance can be empty

    action = agent.act("Something about airplanes would be funnier.") #utterance can be empty?
    print(action)

    agent.save()
    agent2 = OpenAITextChatSamplingAgent(save_path="./",temperature_jump=0.3)
    agent2.load_from_saved_data(agent.file_name)
    action = agent2.resample()
    print(action)
    agent2.save()


