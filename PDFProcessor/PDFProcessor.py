import os
import re
from pathlib import Path
from llm.llm import LLMChat
import llm.prompt as prompt
from PDFProcessor.PDFTextExtractor import PDFTextExtractor
from PDFProcessor.PDFHighlighter import PDFHighlighter
from PDFProcessor.PDFRedactor import PDFRedactor
import logging, logging.config
import pymupdf4llm
from tqdm import tqdm
from datetime import datetime

class PDFProcessor:
  def __init__(self, conf: dict, pdf_path: Path, output_pdf_path: Path):
    self.conf = conf
    self.pdf_path = pdf_path
    self.output_pdf_path = output_pdf_path
    self.words = []
    self.obf_words = []

  # File system access methods
  def save_words(self, output_path: Path) -> None:
    """
    saves the words to redact in a file in cache folder
    format: word, obfuscated_word\n
    """
    with open(output_path, "w") as f:
      for idx in range(len(self.words)):
        f.write(f"{self.words[idx]}, {self.obf_words[idx]}\n")

  def load_words(self, input_path: Path) -> None:
    """ 
    loads the words to redact from a file in cache folder
    format: word, obfuscated_word\n
    """
    with open(input_path, "r") as f:
      content = f.readlines()
      for line in content:
        self.words.append(line.split(", ")[0])
        self.obf_words.append(line.split(", ")[1])

  # Word processing method
  def apply_filters(self) -> None:
    """
    This function is used to apply filters to the detected words.
    removing words with not allowed characters and adding new date formats
    """
    for word in self.words:
      # Check for not allowed chars
      if any(char in word for char in self.conf["NOT_ALLOWED_CHARS"]):
        # remove the word
        self.words.remove(word)
      
      # Check for date formats
      new_date = new_date_format(word)
      if new_date:
        self.words.append(new_date)

  # LLM inference methods
  def process_batches(self, detective: LLMChat, batches: list, temperature: int) -> None:
    """
    Feeds the batches to LLM and processes the response

    Example response: "word1, word2, word3, None, word4, word5"
    
    Removes None, duplicates and words shorter than 3 characters
    Adds the responses to words list
    """
    total_batches = len(batches)
    for idx, batch in tqdm(enumerate(batches), total=total_batches, desc="elaborating batches", dynamic_ncols=True):
      resp = detective.generate_response(prompt.DETECTION_INSTRUCTION_V8, prompt.EXAMPLES_ARR, batch, temperature)
      if os.getenv("DEBUG") == "1":
        print(f"llm response: n {idx} of {len(batches)} \n{resp}")
      splitted = [item.strip() for item in resp.split(",")]
      for item in splitted:
        if item != "None" and len(item) > self.conf['MIN_LENGTH']:   # Ignore short words and "None"
          self.words.append(item)
    self.words = list(set(self.words))  # Remove duplicates

  def obfuscate_words(self, model: LLMChat, temp=1) -> None:
    """
    Obfuscates the words in doc object using LLM model
    Adds the response to obf_words list
    """
    for word in self.words:
      response = model.generate_response(prompt.REDACTION_INSTRUCTION_V1, prompt.EXAMPLES_ARR_REDACTION, word, temperature=temp)
      if os.getenv("DEBUG")=="1": print(response)
      #assert word != response  # Response must be different from the input
      if word == response:
        response = " "
      self.obf_words.append(response)

  # PDF pipeline
  def process_pdf(self, llm: LLMChat, temperature: int, mode: str) -> None:
    """
    Main pipeline for PDF processing
    """
    if mode == "dry-run":
      text_processor = PDFTextExtractor(self.pdf_path)
      
      # Extract text
      text = text_processor.extract_text()
      batches = text_processor.split_text_into_batches(text, self.conf['MAX_BATCH_SIZE'])
    
      # LLM inference
      self.process_batches(llm, batches, temperature)
      if os.getenv("DEBUG")=="1": print(self.words)

      # Apply constraints to detected words
      self.apply_filters()
      if os.getenv("DEBUG")=="1": print(f"after filter: {self.words}")
    
      # Obfuscate words
      if self.conf['TARGET_WORDS'] == "None":
        print("obfuscating words...")
        self.obfuscate_words(llm)
        if os.getenv("DEBUG")=="1": print(f"obfuscated words: {self.obf_words}")
      else:
        for word in self.words:
          self.obf_words.append(self.conf['TARGET_WORDS'])

      # Save words with the respective obfuscation to the fs
      print(f"saving words to {self.conf['WORDS_PATH']}...")
      filename = extract_filename(self.pdf_path)
      self.save_words(self.conf['WORDS_PATH'] / f"{filename}.txt")

      # highlight the words to redact
      print("performing highlight...")
      highlighter = PDFHighlighter(self.pdf_path, self.words, self.obf_words) 
      highlighter.highlight(self.output_pdf_path, self.conf['HIGHLIGHT_COLOR'], opacity=self.conf["OPACITY"])

    elif mode == "redaction":
      try:
        # Load words from cache
        print(f"loading obfuscated words from {self.conf['WORDS_PATH']}...")
        self.load_words(self.conf['WORDS_PATH'] / f"{extract_filename(self.pdf_path)}.txt")
        if self.conf["TARGET_WORDS"] != "None":
          self.obf_words = [self.conf["TARGET_WORDS"] for _ in range(len(self.words))]
        if os.getenv("DEBUG") == "1": print(f"obfuscated words: {self.words} --> {self.obf_words}")

        # Perform redaction on the PDF
        print("performing PDF redaction...")
        redactor = PDFRedactor(self.pdf_path, self.words, self.obf_words)
        if self.conf["REDACTION"] == "pdf_redactor":
          redactor.redact_with_pdf_redactor(self.output_pdf_path)
        else:
          redactor.redact_words(self.output_pdf_path,
                                self.conf["METADATA"],
                                self.conf["BACKGROUND_COLOR"],
                                self.conf["TEXT_COLOR"],
                                self.conf["FONT_SIZE"])
      
      except FileNotFoundError:
        print(f"{self.pdf_path} not found in cache, try running in dry-run mode first")
    
    else:
      raise ValueError("Invalid mode, please choose between 'dry-run' and 'redaction'")




# Helper functions

def new_date_format(date_str: str) -> str:
  """
  Checks if a date in format '01 January 1958'.
  If the input is not in the expected format, it returns None.
  Returns:
  str: The date string in 'DD/MM/YYYY' format or None input if validation fails.
  TODO: Add more date formats and it should also work the opposite way
  """
  # Regular expression to match the expected date format
  date_pattern = r"^\d{2}\s(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}$"
    
  if re.match(date_pattern, date_str):
    try:
      # Parse the date using datetime
      date_obj = datetime.strptime(date_str, "%d %B %Y")
      # Format the date as 'DD/MM/YYYY'
      return date_obj.strftime("%d/%m/%Y")
    except ValueError:
      return None
  else:
    return None
  
def redact_md(input_md_path: Path, output_md_path: Path) -> None:
  """
  extracts text from redacted PDF and saves it in markdown format to the markdown folder path md_out/
  NOT USED
  """
  md_text = pymupdf4llm.to_markdown(input_md_path)
  output_md_path.write_bytes(md_text.encode())

# from a path extract the filename without extension
def extract_filename(path: Path) -> str:
  return path.stem
