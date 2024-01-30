import alfworld
import alfworld.agents.environment
import yaml




PREFIXES = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
}




if __name__=="__main__":
    with open('playgrounds/base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    split = "eval_out_of_distribution"

    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)

    ob, info = env.reset()
    ob = '\n'.join(ob[0].split('\n\n')[1:])
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
    
    print(ob)
    print(info)
    print(name)

    game_running_flag = True
    while game_running_flag:
        action = input(">")
        observation, reward, done, info = env.step([action])
        print(observation)
        print(info["won"][0])
        print(done)