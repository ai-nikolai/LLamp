

if [ $1 == "test" ]; then
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        # --end_index \
fi;


if [ $1 == "test_ours" ]; then
    var='["prompt","plan"]'
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "ours" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0301" \
        --trial_name "v3_1_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --keys_to_remove $var
        # --end_index \
fi;






if [ $1 == "eval" ]; then
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_full" \
        --start_index 0 \
        --num_envs 135 \
        # --end_index \
fi;





if [ $1 == "test_all" ]; then
    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "ours" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "agentbench" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "jsonreact" \
        --llm_type "OpenAIChatText" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIChatTextSampling" \
        --model "gpt-3.5-turbo-0125" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "OpenAIText" \
        --model "gpt-3.5-turbo-instruct" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \

    python3 playgrounds/playground_alfworld_eval.py \
        --agent "react" \
        --llm_type "CohereChat" \
        --model "command-r-plus" \
        --trial_name "v3_0_eval_test" \
        --start_index 0 \
        --num_envs 1 \
        --force_run
        # --end_index \
fi;