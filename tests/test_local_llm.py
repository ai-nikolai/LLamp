  
from llamp.llms.local import (
    VLLMChat
)

if __name__=="__main__":
    model = "Qwen/Qwen2.5-0.5B-Instruct"
    agent = VLLMChat(
        model=model,
        tensor_parallel_size=1,
        temperature=0.5
    )    
    
    print("\nTesting the act method:")   
    response, token_info = agent.act("Hi", return_token_count=True)
    print(f"\nResponse:\n{response}")
    print(f"\nToken Information:")
    print(f"Input Tokens: {token_info['in_token_all']}")
    print(f"Message Tokens: {token_info['in_token_message']}")
    print(f"Output Tokens: {token_info['out_token_action']}")
    # agent.save()
