from llamp.utils import cohere_model, openai_model

from alfworld_prompts_utils import clean_simple_goal_plan_1, \
cool_simple_goal_plan_1, \
examine_simple_goal_plan_1, \
heat_simple_goal_plan_1, \
clean_state_goal_plan_1, \
clean_state_goal_plan_v2_1, \
clean_state_goal_plan_v3_1, \
clean_state_goal_plan_v4_1, \
clean_state_goal_plan_v4b_1


cohere = cohere_model()

result = cohere(prompt=f"""
Please generate the same kind of annotation as this:
<<<
{clean_state_goal_plan_v4c_1}
>>>

For the following trace:
<<<
            'You are in the middle of a room. Looking quickly around you, '
            'you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a '
            'cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, '
               'a cabinet 1, a coffeemachine 1, a countertop 3, a countertop '
               '2, a countertop 1, a diningtable 1, a drawer 6, a drawer 5, a '
               'drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a '
               'garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a '
               'stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster '
               '1.\n'
               'Your task is to: heat some egg and put it in diningtable.\n'
               '> open fridge 1\n'
               'You open the fridge 1. The fridge 1 is open. In it, you see a '
               'lettuce 2, a mug 2, and a potato 3.\n'
               '> go to countertop 1\n'
               'On the countertop 1, you see a bread 1, a fork 1, and a '
               'saltshaker 1.\n'
               '> go to countertop 2\n'
               'On the countertop 2, you see nothing.\n'
               '> go to countertop 3\n'
               'On the countertop 3, you see a bowl 1, a butterknife 1, a egg '
               '2, a kettle 2, a plate 1, a sink 1, and a spatula 2.\n'
               '> take egg 2 from countertop 3\n'
               'You pick up the egg 2 from the countertop 3.\n'
               '> go to microwave 1\n'
               'The microwave 1 is closed.\n'
               '> heat egg 2 with microwave 1\n'
               'You heat the egg 2 using the microwave 1.\n'
               '> go to diningtable 1\n'
               'On the diningtable 1, you see a apple 2, a bread 3, a egg 1, a '
               'kettle 1, a knife 1, a mug 1, a papertowelroll 1, a '
               'peppershaker 2, a potato 1, a soapbottle 1, and a spatula 1.\n'
               '> put egg 2 in/on diningtable 1\n'
               'You put the egg 2 in/on the diningtable 1.\n',
>>>
"""
)

print(result)