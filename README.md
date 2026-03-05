# PDF Watermark Remover

A command-line tool to remove text watermarks from PDF files.

It works by locating the watermark text in each page's content stream and
stripping the surrounding graphics block — leaving the rest of the page
untouched.

## Requirements

- Python 3.8+
- [pikepdf](https://pikepdf.readthedocs.io/)

## Setup

### Using uv (recommended)

[uv](https://docs.astral.sh/uv/) creates the virtual environment and installs
dependencies in one step.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo
git clone https://github.com/evohnave/pdf-watermark-remover.git
cd pdf-watermark-remover

# Create venv and install dependencies
uv sync
```

Optionally, install the tool itself so `remove-watermark` is available
anywhere in the venv:

```bash
uv pip install -e .
```

Run the script without activating the venv:

```bash
uv run remove_watermark.py input.pdf "Watermark Text"
```

### Using pip

```bash
# Clone the repo
git clone https://github.com/evohnave/pdf-watermark-remover.git
cd pdf-watermark-remover

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

Optionally, install the tool itself so `remove-watermark` is available
anywhere in the venv:

```bash
pip install -e .
```

## Usage

```bash
python3 remove_watermark.py input.pdf "Watermark Text"
```

By default the cleaned file is saved as `input_clean.pdf` in the same
directory. Use `-o` to specify a different output path:

```bash
python3 remove_watermark.py input.pdf "Academia.edu" -o output.pdf
```

If installed via `pip install -e .`:

```bash
remove-watermark input.pdf "Academia.edu"
```

### Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input PDF |
| `watermark` | Exact watermark text to remove |
| `-o`, `--output` | Output path (default: `<input>_clean.pdf`) |

## How it works

PDF watermarks added by services like Academia.edu are injected directly into
each page's content stream as a text drawing command. The script:

1. Opens each page's content stream
2. Decompresses it (FlateDecode)
3. Uses a regex to find and remove the `q ... (WatermarkText)Tj ... Q` block
4. Recompresses and saves

## License

MIT
