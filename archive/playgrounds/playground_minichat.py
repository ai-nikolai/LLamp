import torch
import transformers


if __name__=="__main__":
    if torch.cuda.is_available():
        torch.set_default_device("cuda")
    elif torch.backends.mps.is_available():
        mps_device = torch.device("mps")    
    else:
        torch.set_default_device("cpu")

    # mps_device = torch.device("mps")    
        
    model = transformers.AutoModelForCausalLM.from_pretrained("GeneZC/MiniChat-3B", device_map='auto', use_cache=True, torch_dtype=torch.float16)
    # https://github.com/huggingface/transformers/issues/27132
    # please use the slow tokenizer since fast and slow tokenizer produces different tokens
    tokenizer = transformers.AutoTokenizer.from_pretrained(
            "GeneZC/MiniChat-3B",
            use_fast=False
        )
    if mps_device:
        model.to(mps_device)


    # system_message = "You are Orca, an AI language model created by Microsoft. You are a cautious assistant. You carefully follow instructions. You are helpful and harmless and you follow ethical guidelines and promote positive behavior."
    # user_message = "How can you determine if a restaurant is popular among locals or mainly attracts tourists, and why might this information be useful?"


    # <s>[|System|] Answer three words, including a Hello. [|User|] Yes? </s>[|Assistant|]
    
    system_message ="Answer one word."
    user_message="Yes?"
    # prompt = f"<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant"
    prompt = f"<s>[|System|]{system_message}[|User|]{user_message}</s>[|Assistant|]"

    if mps_device:
        inputs = tokenizer(prompt, return_tensors='pt').to(mps_device)
    else:
        inputs = tokenizer(prompt, return_tensors='pt')

    output_ids = model.generate(inputs["input_ids"],)
    answer = tokenizer.batch_decode(output_ids)[0]

    print(answer)

    # # This example continues showing how to add a second turn message by the user to the conversation
    # second_turn_user_message = "Give me a list of the key points of your first answer."

    # # we set add_special_tokens=False because we dont want to automatically add a bos_token between messages
    # second_turn_message_in_markup = f"\n<|im_start|>user\n{second_turn_user_message}<|im_end|>\n<|im_start|>assistant"
    # second_turn_tokens = tokenizer(second_turn_message_in_markup, return_tensors='pt', add_special_tokens=False)
    # second_turn_input = torch.cat([output_ids, second_turn_tokens['input_ids']], dim=1)

    # output_ids_2 = model.generate(second_turn_input,)
    # second_turn_answer = tokenizer.batch_decode(output_ids_2)[0]

    # print(second_turn_answer)
