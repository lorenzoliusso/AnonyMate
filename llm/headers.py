BOT = "<|begin_of_text|>"
S_HEADER = "<|start_header_id|>"
E_HEADER = "<|end_header_id|>"
EOT = "<|eot_id|>"


def generate_llama_prompt(prompt: str, pre_prompt: str, examples_arr: list) -> str:
  """
  LLAMA-3 prompt format

  Given a prompt, pre_prompt and a list of examples, return a string with the correct llama headers.
  This is the last step in prompt processing before feeding the model.
  See https://www.llama.com/docs/model-cards-and-prompt-formats/meta-llama-3/#llama-3-instruct
  """
  examples = ""
  for item in examples_arr:
    user_prompt = item["user"]
    assistant_response = item["assistant"]
    examples += f"{S_HEADER}user{E_HEADER}\n\n{user_prompt}{EOT}\n{S_HEADER}assistant{E_HEADER}\n\n{assistant_response}{EOT}\n"

  return (
    f"{BOT}{S_HEADER}system{E_HEADER}\n\n"
    f"{pre_prompt}{EOT}\n"
    f"{examples}"
    f"{S_HEADER}user{E_HEADER}\n\n"
    f"{prompt}{EOT}\n"
    f"{S_HEADER}assistant{E_HEADER}\n\n"
  )


def generate_mixtral_prompt(prompt: str, pre_prompt: str, examples_arr: list) -> str:
  """
  Mixtral prompt format
  See https://huggingface.co/mistralai/Ministral-8B-Instruct-2410
  """
  examples = ""
  for item in examples_arr:
    user_prompt = item["user"]
    assistant_response = item["assistant"]
    examples += f"[INST]{user_prompt}[/INST][INST]{assistant_response}[/INST]\n"

  return (
    f"<s>[INST]{pre_prompt}[/INST]\n"
    f"{examples}"
    f"[INST]{prompt}[/INST]<s>\n"
  )