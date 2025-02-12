import gym
import textworld.gym

# Register a text-based game as a new Gym's environment.
env_id = textworld.gym.register_game("games/zork_games/zork1.z5")

env = gym.make(env_id)  # Start the environment.

obs, infos = env.reset()  # Start new episode.
env.render()
print(infos)


score, moves, done = 0, 0, False
while not done:
    command = input("> ")
    obs, score, done, infos = env.step(command)
    env.render()
    print(score)

    moves += 1

env.close()
print("moves: {}; score: {}".format(moves, score))