# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (recommended)
uv sync

# Run the tool
uv run remove_watermark.py input.pdf "Watermark Text"
uv run remove_watermark.py input.pdf "Watermark Text" -o output.pdf

# Install as CLI entrypoint
uv pip install -e .
remove-watermark input.pdf "Watermark Text"
```

## Architecture

This is a single-file CLI tool (`remove_watermark.py`) with no tests. The entry point is `main()`, registered as the `remove-watermark` console script via `pyproject.toml`.

**Core pipeline:**

1. `build_pattern(watermark_text)` — constructs a regex that matches a PDF graphics save/restore block (`q...Q`) containing the watermark's `(text)Tj` operator. Handles one level of nesting.
2. `get_stream_bytes(stream)` — reads a pikepdf stream and attempts zlib decompression, returning `(bytes, was_compressed)`.
3. `write_stream_bytes(stream, data, compressed)` — re-encodes the stream, reapplying FlateDecode if the original was compressed.
4. `remove_watermark(input_path, watermark_text, output_path)` — iterates pages, resolves `/Contents` (which may be a single stream or an `Array` of streams), applies the regex substitution, and saves only if matches were found.

**Key constraint:** The regex operates on raw PDF content stream bytes (latin-1 encoded). Watermark text is escaped with `re.escape` after encoding to latin-1. The pattern assumes the watermark is rendered via a `(text)Tj` operator inside a `q...Q` graphics state block.
