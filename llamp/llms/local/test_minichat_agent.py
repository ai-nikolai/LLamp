from llamp.llms.local.minichat import MiniChat

if __name__=="__main__":
    agent = MiniChat(test_mode=True)
    # agent.add_first_observation("Yes?")

    agent.act("yes?")

    prompt = agent.construct_prompt_for_model()
    print(prompt)