from llamp.llms.base_llm_system import BaseLLMSystem
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams


class VLLMChat(BaseLLMSystem):
    def __init__(self, system_name="VLLMChat", save_path="game_logs", temperature=0.0, model="Qwen/Qwen2.5-7B-Instruct", tensor_parallel_size=1, max_model_len=16000):
        super().__init__(system_name, save_path, temperature=temperature)
        
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.sampling_params = SamplingParams(
            temperature=temperature,
            top_p=1.0,
            repetition_penalty=1.00,
            max_tokens=2000
        )
        self.llm = LLM(
            model=model,
            tensor_parallel_size=tensor_parallel_size,
            gpu_memory_utilization=0.95,
            max_model_len=max_model_len,
            dtype="auto"
        )
        print("="*20)
        print(f"Model loaded as: {model} with tensors: {tensor_parallel_size}")

    def call_model(self, temperature=None):
        prompt = self.generate_text_prompt()
        messages = [
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        outputs = self.llm.generate([text], self.sampling_params)
        return outputs[0].outputs[0].text

    def count_tokens(self, optional_text=None, model_name=None):
        if optional_text:
            return len(self.tokenizer.encode(optional_text))
        else:
            prompt = self.generate_text_prompt()
            return len(self.tokenizer.encode(prompt))


if __name__=="__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run QwenLLM System')
    parser.add_argument('--model', type=str, default="Qwen/Qwen2.5-7B-Instruct",
                        choices=["Qwen/Qwen2.5-7B-Instruct", 
                                "Qwen/Qwen2.5-14B-Instruct",
                                "Qwen/Qwen2.5-32B-Instruct",
                                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                                "mistralai/Mixtral-8x22B-Instruct-v0.1",
                                ],
                        help='Model to use')
    parser.add_argument('--num_gpus', type=int, default=1,
                        help='Number of GPUs to use for tensor parallelism')
    parser.add_argument('--temperature', type=float, default=0.7,
                        help='Temperature for sampling')
    parser.add_argument('--test_prompt', type=str, 
                        default="Tell me a short story about a robot learning to paint.",
                        help='Test prompt to try')
    
    args = parser.parse_args()
    
    system = VLLMChat(
        model=args.model,
        tensor_parallel_size=args.num_gpus,
        temperature=args.temperature
    )
    
    print("\nTesting the act method:")
    response, token_info = system.act(args.test_prompt, return_token_count=True)
    print(f"\nResponse:\n{response}")
    print(f"\nToken Information:")
    print(f"Input Tokens: {token_info['in_token_all']}")
    print(f"Message Tokens: {token_info['in_token_message']}")
    print(f"Output Tokens: {token_info['out_token_action']}")
    system.save()

    # print(f"\nTesting with prompt: {args.test_prompt}")
    # system.add_message("user", args.test_prompt)
    # response = system.call_model()
    # print(f"\nResponse:\n{response}")
    
    # token_count = system.count_tokens()
    # print(f"\nToken count: {token_count}")
