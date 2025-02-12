import gymnasium as gym


env = gym.make("MiniGrid-MultiRoom-N2-S4-v0",render_mode="human")  # Start the environment.

obs, infos = env.reset()  # Start new episode.
# env.render()
# print(obs)
# print("+=+="*20)
# print(infos)

score, moves, done = 0, 0, False
while not done:
    command = input("> ")
    obs, score, done, infos = env.step(command)
    env.render()
    # print(obs)
    # print("1+=+="*20)
    # print(score)
    # print("2+=+="*20)
    # print(done)
    # print("+=+="*20)
    # print(infos)

    moves += 1

env.close()
print("moves: {}; score: {}".format(moves, score))