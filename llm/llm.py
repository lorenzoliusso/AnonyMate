import os
from vllm import SamplingParams, LLM
import llm.headers as headers

CACHE_PATH = "/mnt/dmif-nas/SMDC/HF-Cache/"

class LLMChat:
  """
  Wrapper for the LLM model.
  """
  def __init__(self, args):
    #print(f"using {args.model}...")
    self.args = args
    self.llm_engine = LLM(model=args.model,
                          dtype="auto",
                          gpu_memory_utilization=0.75,
                          max_model_len=args.count,
                          download_dir=CACHE_PATH,
                          disable_log_stats=True)

  def generate_response(self, pre_prompt: str, examples: list, prompt: str, temperature: float = 0.0) -> str:
    """
    Generate a response from the model given a prompt and examples."""

    sampling_params = SamplingParams(temperature=temperature, max_tokens=self.args.count)

    # Generate the correct prompt format for the model (only two models supported for now)
    if self.args.model == "mistralai/Ministral-8B-Instruct-2410":
      pr = headers.generate_mixtral_prompt(prompt, pre_prompt, examples)
    else:
      pr = headers.generate_llama_prompt(prompt, pre_prompt, examples)
    
    if os.getenv("DEBUG")=="2":
      print("\nPrompt:", pr)
    elif os.getenv("DEBUG")=="1":
      print("\nPrompt:", prompt)

    results = self.llm_engine.generate(pr, sampling_params=sampling_params, use_tqdm=True if os.getenv("DEBUG")=="3" else False)
    
    if isinstance(prompt, str):
      return results[0].outputs[0].text
    else:
      return [result.outputs[0].text for result in results]
