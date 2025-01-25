from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import argparse


class QwenLLMMultiGPU():

    def __init__(self, model_name="Qwen/Qwen2.5-32B-Instruct", tensor_parallel_size=1, max_model_len=16000):
        # Initialize the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Pass the default decoding hyperparameters of Qwen2.5-7B-Instruct
        # max_tokens is for the maximum length for generation.
        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=512)

        # Input the model name or path. Can be GPTQ or AWQ models.
        self.llm = LLM(model=model_name, tensor_parallel_size=tensor_parallel_size, gpu_memory_utilization=0.95, max_model_len=max_model_len, dtype="auto")
        print("="*20)
        print(f"Model loaded as: {model_name} with tensors: {tensor_parallel_size}")

    def call_llm(self,prompt):
        """Calls the llm and does stuff"""
        # Prepare your prompts
        messages = [
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # generate outputs
        outputs = self.llm.generate([text], self.sampling_params)

        # Print the outputs.
        for output in outputs:
            prompt = output.prompt
            generated_text = output.outputs[0].text
            print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser(description='GPU Count for QWEN')
    parser.add_argument('--gpus', type=int, default=1, help='Number of GPUs (default: 1)')
    args = parser.parse_args()

    prompt = "Tell me something about large language models."
    llm = QwenLLMMultiGPU(tensor_parallel_size=args.gpus)
    llm.call_llm(prompt)
