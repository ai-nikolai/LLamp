keys_to_use='["goal","current_location","current_inventory","thought","action"]'
python3 test.py \
--agent "ours-text" \
--llm_type "CerebrasChatText" \
--model "llama3.1-8b" \
--trial_name "v4_1_6_test" \
--start_index 0 \
--num_envs 1 \
--keys_to_use $keys_to_use \
--prompt_ids 1 0 \
--apply_correction \
--force_run
