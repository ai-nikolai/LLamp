

if [ $1 == "test" ]; then
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        # --end_index \

fi;


if [ $1 == "test_ours" ]; then
    keys_to_use='["goal","thought","locations_visited","action"]'
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "ours" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-1106" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --prompt_ids 0 1 \
        --keys_to_use $keys_to_use
        # --end_index \

fi;


if [ $1 == "test_ours_full" ]; then
    keys_to_use='["goal","thought","action"]'
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "ours" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-1106" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 10 \
        --keys_to_use $keys_to_use \
        --prompt_ids 0 1 \
        --apply_correction \
        --force_run
        # --end_index \

fi;



if [ $1 == "test_all" ]; then
    keys_to_use='["goal","thought","locations_visited","action"]'
    echo "=============================="
    echo "Running react with turbo-0125"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --prompt_ids 2 0 1 \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running ours with turbo-0125"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "ours" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --keys_to_use $keys_to_use \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running agentbench with turbo-0125"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "agentbench" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running jsonreact with turbo-0125, version 2"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "jsonreact" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --agent_version 2 \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running react with turbo-0125, with sampling llm"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatTextSampling" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running react with turbo-0125, with instruct llm"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIText" \
        --model "gpt-3.5-turbo-instruct" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    echo "=============================="
    echo "Running react with turbo-0125 with command-r-plus"
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "CohereChat" \
        --model "command-r-plus" \
        --trial_name "v3_3_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

fi;




if [ $1 == "eval" ]; then
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_3_eval_full" \
        --start_index 0 \
        --num_envs 135 \
        # --end_index \

fi;