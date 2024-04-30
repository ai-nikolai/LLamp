from llamp.minichat_agent import MiniChatAgent

if __name__=="__main__":
    agent = MiniChatAgent(test_mode=True)
    # agent.add_first_observation("Yes?")

    agent.act("yes?")

    prompt = agent.construct_prompt_for_model()
    print(prompt)