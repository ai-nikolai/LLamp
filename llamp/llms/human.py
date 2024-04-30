from llamp.llms.base_system import BaseSystem

class Human(BaseSystem):
    def __init__(self, system_name="Human",save_path="game_logs"):
        super().__init__(system_name, save_path)
   

    def call_model(self):
        """The action is just whatever the user inputs"""
        action = input("[[INPUT YOUR ACTION]] >>")
        return action     


if __name__=="__main__":
    print("Nothing to run here.")
