import re
import json
from pathlib import Path
import PDFProcessor.pdf_redactor as pdf_redactor
import fitz

class PDFRedactor:
  def __init__(self, pdf_path: Path, words: list, obf_words: list):
    self.pdf_path = pdf_path
    self.words = words
    self.obf_words = obf_words

  def redact_words(self, output_path, metadata: str, back_color: tuple, text_color: tuple, font_size: int) -> None:
    """
    redacts the words in the PDF using PyMuPDF library
    """
    if len(self.words) != len(self.obf_words):
      raise ValueError("The number of words to redact must match the number of replacements.")

    doc = fitz.open(self.pdf_path)
    print(f"redacting {len(self.words)} words in {self.pdf_path}")
        
    # metadata redaction
    if metadata == "clear":
      doc.set_metadata({})  # Clear all metadata
    elif metadata == "redact":
      metadata = doc.metadata
      sensitive_keys = ["author", "title", "subject", "producer", "creator"]
      for key in sensitive_keys:
        if key in metadata:
          metadata[key] = "REDACTED"
        doc.set_metadata(metadata)
    elif metadata == "keep":
      pass
    else:
      raise ValueError(f"Invalid value for METADATA: {metadata}")

    patterns = [re.compile(rf"\b{re.escape(word)}\b") for word in self.words]

    for page in doc:
      text = page.get_text("text")
      for replacement_word, pattern in zip(self.obf_words, patterns):
        matches = list(pattern.finditer(text))
        for match in matches:
          areas = page.search_for(match.group())
          for area in areas:
            page.add_redact_annot(area, fill=back_color) 
            rect = fitz.Rect(area)  # Get bounding rectangle
            page.apply_redactions()  # Apply redactions first
            text_position = fitz.Point(rect.x0, rect.y0 + (rect.height / 2) + 2)
            page.insert_text(text_position,
                            replacement_word,
                            color=text_color,  # (0.243, 0.298, 0.341)
                            fontsize=font_size,
                            render_mode=0)
      page.apply_redactions()
    doc.save(output_path)


  # REDACTION USING PDF REDACTOR 
  def generate_filters(self) -> list:
    """  NOT USED
    Generates a list of filters to redact the words in the response (pdf-redactor format)
    example: [(re.compile("word", re.IGNORECASE), lambda m: "####")]
    """
    filters = []
    for target_word, replacement_word in zip(self.words, self.obf_words):
      print(target_word, replacement_word)
      sensible_value = re.escape(target_word)
      filters.append((re.compile(f"{sensible_value}", re.IGNORECASE), lambda m, replacement=replacement_word: replacement[:len(m.group(0))]))
    return filters


  def redact_with_pdf_redactor(self, output_pdf_path: Path, metadata_filters, text_filters, link_filters):
    """
    redacts the PDF using using https://github.com/JoshData/pdf-redactor 
    input: metadata_filters, text_filters, link_filters and output pdf path
    """
    options = pdf_redactor.RedactorOptions()
    options.input_stream = open(str(self.pdf_path), "rb")
    options.output_stream = open(str(output_pdf_path), "wb")

    options.xmp_filters = [lambda xml : None]  # Clear any XMP metadata, if present.
    options.metadata_filters = metadata_filters
    options.content_filters = text_filters
    options.link_filters = link_filters

    pdf_redactor.redactor(options)  # Perform the redaction using PDF on standard input and writing to standard output.


def generate_filters_json(response: str) -> list:
  """   NOT USED
  Generates a list of filters to redact words in the response (pdf-redactor format)
  Example: [(re.compile("word", re.IGNORECASE), lambda m: "####")]
  """
  try:
    response = json.loads(response)
    filters = []
    for entry in response["entries"]:
      if entry["text"]:
        sensible_value = re.escape(entry["text"])
        filter_correction = entry["replacement"]
        filters.append((re.compile(f"{sensible_value}", re.IGNORECASE), lambda m: filter_correction))
  except json.JSONDecodeError as e:
    print(f"\nError decoding JSON response from LLaMA: {e}")
  return filters

