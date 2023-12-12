from .base_agent import BaseAgent

class HumanAgent(BaseAgent):
    def __init__(self, agent_name="HumanAgent",save_path="game_logs"):
        super().__init__(agent_name, save_path)
   

    def call_model(self):
        """The action is just whatever the user inputs"""
        action = input("[[INPUT YOUR ACTION]] >>")
        return action     


if __name__=="__main__":
    print("Nothing to run here.")
