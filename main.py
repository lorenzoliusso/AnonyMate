import argparse
import os
from pathlib import Path
from PDFProcessor.PDFProcessor import PDFProcessor
from llm.llm import LLMChat
import time
import logging
import configparser
from ast import literal_eval

def init_logger():
  global root_logger
  logging.config.fileConfig('anonymizer.conf')
  root_logger = logging.getLogger("main_logger")

def load_conf():
  config = configparser.ConfigParser()
  config.read_file(open('anonymizer.conf'))
  params = dict()

  params.update({"MAX_BATCH_SIZE": int(config.get('dry_run_mode', 'MAX_BATCH_SIZE'))})
  params.update({"WORDS_PATH": Path(config.get('general_parameters', 'WORDS_PATH'))})
  params.update({"TARGET_WORDS": config.get('redaction_mode', 'TARGET_WORDS')})
  params.update({"NOT_ALLOWED_CHARS": config.get('dry_run_mode', 'NOT_ALLOWED_CHARS')})
  params.update({"MIN_LENGTH": int(config.get('dry_run_mode', 'MIN_LENGTH'))})
  params.update({"HIGHLIGHT_COLOR": literal_eval(config.get('dry_run_mode', 'HIGHLIGHT_COLOR'))})
  params.update({"OPACITY": float(config.get('dry_run_mode', 'OPACITY'))})
  params.update({"REDACTION": config.get('redaction_mode', 'REDACTION')})
  params.update({"BACKGROUND_COLOR": literal_eval(config.get('redaction_mode', 'BACKGROUND_COLOR'))})
  params.update({"TEXT_COLOR": literal_eval(config.get('redaction_mode', 'TEXT_COLOR'))})
  params.update({"FONT_SIZE": int(config.get('redaction_mode', 'FONT_SIZE'))})
  params.update({"METADATA": config.get('redaction_mode', 'METADATA')})

  return params

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Run LLama Anonimyzer", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--mode", type=str, default="dry-run", help="dry-run: only model inference, redact: redact the PDFs")
  parser.add_argument("--count", type=int, default=1500, help="Max number of tokens to generate")
  parser.add_argument("--temperature", type=float, default=0.7, help="Temperature in the softmax")
  parser.add_argument("--gen", default="3", help=f"""Generation of the model to use""")  # NOT USED
  parser.add_argument("--size", type=str, default="3B", help=f"""Size of model to use""")  # NOT USED
  parser.add_argument("--model", type=str, default="meta-llama/Llama-3.1-8B-Instruct", help="Hugging Face model to use")
  parser.add_argument("--pdfsrc", type=Path, default=Path("pdf_in"), help="Source path for PDFs")
  parser.add_argument("--pdfdst", type=Path, default=Path("pdf_out"), help="Destination path for PDFs")
  parser.add_argument("--mddst", type=Path, default=Path("md_out"), help="Destination path for MDs")
  args = parser.parse_args()

  # Check if the source folder exists
  if not os.path.exists(args.pdfsrc): raise ValueError("provided source path does not exist")
  if not os.path.exists(args.pdfdst): os.makedirs(args.folderdst)
  #if not os.path.exists(args.mddst): os.makedirs(args.mddst)

  params = load_conf()

  start_time = time.perf_counter()   # Start timer

  # istantiate LLM model only if dry-run mode is selected
  if args.mode == "dry-run":
    llm = LLMChat(args)
  else:
    llm = None

  if args.pdfsrc.is_dir():
    for pdf in os.listdir(args.pdfsrc):
      if pdf.endswith(".pdf"):
        doc = PDFProcessor(params, args.pdfsrc / pdf, args.pdfdst / pdf)
        doc.process_pdf(llm, args.temperature, args.mode)
      else:
        print(f"skipping {pdf}")
  else:
    # expeted full file path in psdsrc
    pdf = os.path.basename(args.pdfsrc)
    if pdf.endswith(".pdf"):
      doc = PDFProcessor(params, args.pdfsrc, args.pdfdst)
      doc.process_pdf(llm, args.temperature, args.mode)

  end_time = time.perf_counter()
  elapsed_time = end_time - start_time

  print(f"Total elapsed time: {elapsed_time:.2f} seconds")