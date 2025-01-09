import os
import re
from pathlib import Path
from pdfminer.high_level import extract_text


class PDFTextExtractor:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path

    def extract_text(self) -> str:
        text = extract_text(self.pdf_path).strip().replace("\n", " ")
        return re.sub(r'\s{2,}', ' ', text)

    def split_text_into_batches(self, text: str, max_chars=500) -> list:
        sentences = re.split(r'(?<=[.!?]) +', text)
        batches = []
        current_batch = ""
        for sentence in sentences:
            while len(sentence) > max_chars:
                batches.append(sentence[:max_chars].strip())
                sentence = sentence[max_chars:]
            if not current_batch:
                current_batch = sentence
            elif len(current_batch) + len(sentence) > max_chars:
                batches.append(current_batch.strip())
                current_batch = sentence
            else:
                current_batch += " " + sentence
        if current_batch:
            batches.append(current_batch.strip())
        return batches
