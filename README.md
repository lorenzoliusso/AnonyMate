# AnonyMate

This Python application processes PDF documents to identify and redact sensitive information. It utilizes a language model (LLama or Mistral) to detect specified terms or patterns within PDF text, applies configurable filters, and redacts or highlights sensitive data. Additionally, it generate markdown representations of redacted PDFs for easier analysis and logging.

## Features

- **PDF Text Extraction**: Extracts text from PDFs in manageable batches for processing.
- **Sensitive Data Detection**: Uses LLM language model to identify sensitive terms or patterns based on user-defined criteria.
- **Redaction**: Redacts identified terms or patterns from PDF documents, obscuring sensitive information using LLM.
- **Highlighting**: Optionally changes the background color of specific terms for visual identification without redaction (dry-run mode).
- **Caching**: Caches previously identified words to avoid repetitive model inference.


## Usage

### Step 1: Configure `anonymizer.conf`

Before running the application, edit the `anonymizer.conf` file to define your settings:
- Terms or patterns to redact.
- Redaction mode (highlight or complete removal).
- Paths for source and destination files.

### Step 2: Install Dependencies

Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

### Step 3: Install Hugging Face CLI

Install the required Python libraries using the following command:

```bash
pip install huggingface_hub
huggingface-cli login
```
Log in to your Hugging Face account when prompted to authenticate and request the acces to one of the Llama 3 models (via web).


### Step 4: Run the Application

Run the application in dry-run mode:
```bash
python main.py --mode dry-run --pdfsrc <source-path> --pdfdst <destination-path>
```

Enable debug mode to see in real time detections and redactions:
```bash
DEBUG=1 python main.py --mode dry-run --pdfsrc <source-folder> --pdfdst <destination-path>
```
If the highlighted words are good, you can run the application in redact mode:

```bash
python main.py --mode redaction --pdfsrc <source-path> --pdfdst <destination-path>
```
Otherwise you can edit the .txt file corrisponding to the PDF in the cache folder and run again in dry-run mode to see the new results.

#### Other supoprted parameters:
- --count   Max number of tokens to generate  (dafault 500)
- --temperature   Temperature during detection   (default 0)
- --model   Hugging Face model to use   (default="meta-llama/Llama-3.1-8B-Instruct")

## Requirements

- Python 3.8+
- Dependencies: The following Python libraries are required
  - `pdfminer.six` for text extraction
  - `pdf_redactor` for PDF redaction
  - `PyMuPDF` (accessed via `fitz`) for PDF manipulation and highlighting
  - `argparse`, `os`, `re`, `json`, `pathlib`

You can install the dependencies using the following command:

```bash
pip install pdfminer.six pdf_redactor pymupdf vllama
```
