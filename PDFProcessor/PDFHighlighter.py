import os
import re
from pathlib import Path
import fitz

class PDFHighlighter:
  def __init__(self, pdf_path: Path, words: list, obf_words: list):
    self.pdf_path = pdf_path
    self.words = words
    self.obf_words = obf_words

  def highlight(self, output_path, color=(1, 1, 0), opacity=0.2) -> None:
    """
    highlights the words to redact in the PDF using PyMuPDF library
    """
    doc = fitz.open(self.pdf_path)
    for page_num in doc:
      page_text = page_num.get_text()
      for target_word in self.words:
        text_instances = page_num.search_for(target_word)
        #print(text_instances)
        if text_instances:
          for inst in text_instances:
            page_num.draw_rect(inst, color=color, fill=color, overlay=True, stroke_opacity=0, fill_opacity=opacity)
    doc.save(output_path)

  def highlight_new(self, output_path, color=(1, 1, 0), opacity=0.2) -> None:
    """
    Highlights the words to redact in the PDF using the PyMuPDF library,
    ensuring the word is not part of another word.
    """
    doc = fitz.open(self.pdf_path)
    
    patterns = [re.compile(rf"\b{re.escape(word)}\b") for word in self.words]

    for page in doc:
      text = page.get_text("text")
      for pattern in patterns:
        matches = list(pattern.finditer(text))
        for match in matches:
          areas = page.search_for(match.group())
          if areas:
            for area in areas:
              page.draw_rect(area, color=color, fill=color, overlay=True, stroke_opacity=0, fill_opacity=opacity)
      page.apply_redactions()
    doc.save(output_path)
