from llamp.llms.base_llm_system import BaseLLMSystem
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams


class VLLMChat(BaseLLMSystem):
    def __init__(self, system_name="VLLMChat", save_path="game_logs", temperature=0.0, model="Qwen/Qwen2.5-7B-Instruct", tensor_parallel_size=1, max_model_len=16000, quantization=False, stop_sequences=None):
        super().__init__(system_name, save_path, temperature=temperature)
        
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.max_model_len = max_model_len
        self.temperature = temperature
        self.stop_sequences = stop_sequences
        self.model=model
        self.tensor_parallel_size = tensor_parallel_size

        try:
            self.apply_chat_template("test")
            self.chat_model = True
        except:
            self.chat_model = False


        if not quantization:
            self.llm = LLM(
                model=model,
                tensor_parallel_size=tensor_parallel_size,
                gpu_memory_utilization=0.95,
                max_model_len=max_model_len,
                dtype="auto"
            )
        else:
            self.llm = LLM(
                model=model,
                tensor_parallel_size=tensor_parallel_size,
                gpu_memory_utilization=0.95,
                max_model_len=max_model_len,
                dtype="auto",
                quantization="bitsandbytes", 
                load_format="bitsandbytes"
            )
        print("="*20)
        print(f"Model loaded as: {model} with tensors: {tensor_parallel_size}")

    def apply_chat_template(self,prompt):
        """uses the chat template"""
        messages = [
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt[-self.max_model_len:]}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        return text
    
    def get_sampling_params(self, temperature=None, stop_sequences=None):
        """temperature and stop_sequences not updated yet."""
        sampling_params = SamplingParams(
            temperature=self.temperature,
            top_p=1.0,
            repetition_penalty=1.00,
            max_tokens=min(2000,self.max_model_len),
            stop = self.stop_sequences
        )
        return sampling_params

    def call_model(self, temperature=None):
        prompt = self.generate_text_prompt()

        if self.chat_model:
            text = self.apply_chat_template(prompt)
        else:
            text = prompt
        sampling_params = self.get_sampling_params()

        outputs = self.llm.generate([text], sampling_params)
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
                        # choices=["Qwen/Qwen2.5-7B-Instruct", 
                        #         "Qwen/Qwen2.5-14B-Instruct",
                        #         "Qwen/Qwen2.5-32B-Instruct",
                        #         "mistralai/Mixtral-8x7B-Instruct-v0.1",
                        #         "mistralai/Mixtral-8x22B-Instruct-v0.1",
                        #         ],
                        help='Model to use')
    parser.add_argument('--gpus', type=int, default=1,
                        help='Number of GPUs to use for tensor parallelism')
    parser.add_argument('--max_len', type=int, default=5000,
                        help='Num_Max_len')
    parser.add_argument('--temperature', type=float, default=0.7,
                        help='Temperature for sampling')
    parser.add_argument('--test_prompt', type=str, 
                        default="Tell me a short story about a robot learning to paint.",
                        help='Test prompt to try')
    parser.add_argument("--quantization", type=int, default=0, help="Whether a quantized model is being loaded.")
    # parser.add_argument('--force_model', type=str, 
    #                     default="Tell me a short story about a robot learning to paint.",
    #                     help='Test prompt to try')    
    args = parser.parse_args()
    
    system = VLLMChat(
        model=args.model,
        tensor_parallel_size=args.gpus,
        temperature=args.temperature,
        max_model_len=args.max_len,
        quantization=bool(args.quantization)
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
