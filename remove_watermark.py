#!/usr/bin/env python3
"""
Remove a text watermark from all pages of a PDF.

Usage:
    python3 remove_watermark.py input.pdf "Watermark Text" [-o output.pdf]

The script searches each page's content stream for the watermark text
and removes the surrounding graphics block (q...Q) that contains it.
"""

import argparse
import re
import sys
import zlib
from pathlib import Path

try:
    import pikepdf
except ImportError:
    sys.exit("pikepdf is not installed. Activate your venv or run: pip install pikepdf")


def build_pattern(watermark_text: str) -> re.Pattern:
    """Build a regex that matches a q...Q block containing the watermark text."""
    escaped = re.escape(watermark_text.encode("latin-1"))
    # Match an outer 'q' save block that contains (possibly nested) the watermark Tj call.
    # Handles one level of nesting (q...q...(text)Tj...Q...Q) as well as a flat q...(text)Tj...Q.
    return re.compile(
        rb"q\n" +                          # outer graphics save
        rb"(?:[^q]|q[^q]*Q\n)*?" +        # any content, allowing one inner q...Q
        rb"\(" + escaped + rb"\)Tj\n" +    # the watermark text operator
        rb".*?" +                          # anything up to the closing sequence
        rb"Q\n(?:Q\n)?",                   # one or two closing Q's
        re.DOTALL,
    )


def get_stream_bytes(stream) -> tuple[bytes, bool]:
    """Read a pikepdf stream, returning (raw_bytes, was_compressed)."""
    raw = stream.read_bytes()
    try:
        return zlib.decompress(raw), True
    except Exception:
        return raw, False


def write_stream_bytes(stream, data: bytes, compressed: bool) -> None:
    if compressed:
        stream.write(zlib.compress(data), filter=pikepdf.Name("/FlateDecode"))
    else:
        stream.write(data, filter=[])


def remove_watermark(input_path: str, watermark_text: str, output_path: str) -> int:
    pattern = build_pattern(watermark_text)
    pdf = pikepdf.open(input_path)
    total_removed = 0

    for i, page in enumerate(pdf.pages):
        contents = page.obj.get("/Contents")
        if contents is None:
            continue

        streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]

        for stream in streams:
            data, compressed = get_stream_bytes(stream)
            new_data, n = pattern.subn(b"", data)
            if n:
                total_removed += n
                print(f"  Page {i + 1}: removed {n} watermark block(s)")
                write_stream_bytes(stream, new_data, compressed)

    if total_removed == 0:
        print(f"  Warning: watermark text '{watermark_text}' not found in any page.")
    else:
        pdf.save(output_path)
        print(f"\nSaved: {output_path}")
        print(f"Total blocks removed: {total_removed}")

    return total_removed


def main():
    parser = argparse.ArgumentParser(description="Remove a text watermark from a PDF.")
    parser.add_argument("input", help="Path to the input PDF")
    parser.add_argument("watermark", help="Watermark text to remove (e.g. 'Academia.edu')")
    parser.add_argument(
        "-o", "--output",
        help="Path for the output PDF (default: input_clean.pdf)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"Error: file not found: {input_path}")

    output_path = args.output or str(input_path.with_stem(input_path.stem + "_clean"))

    print(f"Input:     {input_path}")
    print(f"Watermark: {args.watermark!r}")
    print(f"Output:    {output_path}\n")

    remove_watermark(str(input_path), args.watermark, output_path)


if __name__ == "__main__":
    main()
