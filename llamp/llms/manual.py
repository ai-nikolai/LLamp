from llamp.llms.base_system import BaseSystem

class Manual(BaseSystem):
    def __init__(self, system_name="Manual",save_path="game_logs"):
        super().__init__(system_name, save_path)
   

    def call_model(self):
        """The action is just whatever the user inputs"""
        action = input("[[INPUT YOUR ACTION]] >>")
        return action     


if __name__=="__main__":
    agent = Manual()    
    
    print("\nTesting the act method:")   
    response, token_info = agent.act("Hi", return_token_count=True)
    print(f"\nResponse:\n{response}")
    print(f"\nToken Information:")
    print(f"Input Tokens: {token_info['in_token_all']}")
    print(f"Message Tokens: {token_info['in_token_message']}")
    print(f"Output Tokens: {token_info['out_token_action']}")


    response = agent.act("Hi", return_token_count=False)
    print(f"\nResponse:\n{response}")
