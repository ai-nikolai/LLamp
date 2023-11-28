import transformers


model_name = 'Intel/neural-chat-7b-v3-1'
model = transformers.AutoModelForCausalLM.from_pretrained(model_name) #device_map='auto', offload_folder="offload"
tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)


def generate_response(system_input, user_input):
    
    # Format the input using the provided template
    prompt = f"### System:\n{system_input}\n### User:\n{user_input}\n### Assistant:\n"

    # Tokenize and encode the prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Generate a response
    outputs = model.generate(inputs, max_length=1000, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the assistant's response
    return response.split("### Assistant:\n")[-1]


# Example usage
# system_input = "You are a chatbot developed by Intel. Please answer all questions to the best of your ability."
# user_input = "How does the neural-chat-7b-v3-1 model work?"

system_input = "Answer one word."
user_input =  "Yes?"
response = generate_response(system_input, user_input)
print(response)
