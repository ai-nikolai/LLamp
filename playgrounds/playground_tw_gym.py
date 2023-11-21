import gym
import textworld.gym

from llamp.openai_agent import OpenAIAgent
from llamp.orca2_agent import Orca2Agent

# import warnings
# warnings.filterwarnings("ignore")

if __name__=="__main__":

    ####################
    # SET THE AGENT TYPE
    ####################

    # AGENT_TYPE = "openai"
    # AGENT_TYPE = "orca2"
    AGENT_TYPE = "orca2_test"

    ####################
    # Running the Agent
    ####################
    # Register a text-based game as a new Gym's environment.
    env_id = textworld.gym.register_game("games/tw_games/w2_o10_l5_game.z8",
                                         max_episode_steps=50)
    env = gym.make(env_id)  # Start the environment.


    # Load the agent you want:
    if AGENT_TYPE=="openai":
        agent = OpenAIAgent()
    elif AGENT_TYPE=="orca2":
        agent = Orca2Agent()
    elif AGENT_TYPE=="orca2_test":
        agent = Orca2Agent(test_mode=True)
        agent.act("yes?")
        agent.save()
        exit()
    else:
        NotImplementedError("This agent is not implemented.")


    # New Environment and Observations.
    obs, infos = env.reset()  # Start new episode.
    env.render()

    cut_header_index = obs.index("Welcome to TextWorld!")
    first_obs = obs[cut_header_index:]

    command = agent.act(first_obs)
    print(command)

    score, moves, done = 0, 0, False


    try:
        #### MAIN GAME LOOP
        while not done:
            obs, score, done, infos = env.step(command)
            env.render()

            moves += 1
            if moves % 10 == 0:
                done = True
                continue

            command = agent.act(obs)
            print(command)

    finally:
        agent.save()
        env.close()
        print("moves: {}; score: {}".format(moves, score))

