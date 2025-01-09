# AnonyMate

AnonyMate is a simple Python application designed to process PDF documents by identifying and redacting sensitive information. It leverages language models like LLaMA or Mistral using [vLLM](https://docs.vllm.ai/en/latest/) to detect specified terms or patterns within PDF text, apply configurable filters, and redact or highlight sensitive data. It can also generate markdown representations of redacted PDFs for easier analysis and logging.

## Features

- **PDF Text Extraction**: Extracts text from PDFs in manageable batches for efficient processing.
- **Sensitive Data Detection**: Detects sensitive terms or patterns using an LLM based on user-defined criteria.
- **Redaction**: Obscures sensitive terms or patterns in PDF documents with redaction.
- **Highlighting**: Optionally changes the background color of specific terms for visual identification without redaction (dry-run mode).
- **Caching**: Caches previously detected terms to reduce redundant model inferences and speed up processing.


## Usage

### Step 1: Configure `anonymizer.conf`

Before running the application, edit the `anonymizer.conf` file to define your settings.

This settings allow you to configure the behavior of the application, in the two phases of detection and redaction.


```conf
[general_parameters]
MODEL = meta-llama/Llama-3.1-8B-Instruct
PDF_SOURCE = pdf_in
PDF_DESTINATION = pdf_out
WORDS_PATH = cache/


[dry_run_mode]
MAX_BATCH_SIZE = 500
HIGHLIGHT_COLOR = (1, 1, 0)
OPACITY = 0.3
NOT_ALLOWED_CHARS = %%
MIN_LENGTH = 3

[redaction_mode]
TARGET_WORDS = None
REDACTION = PyMuPDF
BACKGROUND_COLOR = (1, 1, 1)
TEXT_COLOR = (0, 0, 0)
FONT_SIZE = 7
METADATA = redact
```

### Step 2: Install Dependencies

Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

### Step 3: Install Hugging Face CLI

Install the Hugging Face CLI tool and log in to access the required language models:

```bash
pip install huggingface_hub
huggingface-cli login
```
During the process, authenticate with your Hugging Face account and request access to the LLaMA 3 models via their web portal if needed.


### Step 4: Run the Application

To test the detection and highlighting of sensitive data:
```bash
python main.py --mode dry-run --pdfsrc <source-path> --pdfdst <destination-path>
```

Enable debug mode to view real-time detection and processing:
```bash
DEBUG=1 python main.py --mode dry-run --pdfsrc <source-folder> --pdfdst <destination-path>
```

If the highlighted words in dry-run mode are accurate, proceed to redact sensitive information:
```bash
python main.py --mode redaction --pdfsrc <source-path> --pdfdst <destination-path>
```

If the detection results need adjustment, edit the .txt files corresponding to the PDF in the cache folder and re-run in dry-run mode to verify changes.

#### Other supoprted parameters:
- `--count` Max number of tokens to generate (dafault 500)
- `--temperature` Temperature during detection (default 0)
- `--model` Hugging Face model to use (default="meta-llama/Llama-3.1-8B-Instruct")

## Requirements

- Python 3.8+
- Dependencies: The following Python libraries are required
  - `pdfminer.six` for text extraction
  - `vllm` for language model inference
  - `pdf_redactor` provides avanced redaction capabilities (still in development) see [here](https://github.com/JoshData/pdf-redactor?tab=readme-ov-file)
  - `PyMuPDF` (accessed via `fitz`) for PDF manipulation and highlighting
  - `argparse`, `os`, `re`, `json`, `pathlib`


