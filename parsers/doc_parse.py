"""Document parsing helpers for PDF and DOCX files.

Functions:
- `extract_text(path)` -> str: extract raw text from `.pdf` or `.docx`.
- `prepare_prompt(text, instruction=None, max_chars=3000)` -> str: produce a prompt string
   suitable for sending to a model (truncates and cleans text).

This module aims to produce plain text ready to pass into Ollama or other LLM backends.
"""
from pathlib import Path
from typing import List, Optional
import re


def _clean_whitespace(s: str) -> str:
    # replace multiple whitespace/newlines with single space, trim
    return re.sub(r"\s+", " ", s).strip()


def extract_text(path: str) -> str:
    """Extract text from a PDF or DOCX file.

    Args:
        path: filesystem path to the file (.pdf or .docx)

    Returns:
        Extracted plain text.

    Raises:
        ValueError for unsupported file types.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()
    if suffix == ".pdf":
        try:
            import pdfplumber
        except Exception as e:
            raise RuntimeError("pdfplumber is required to parse PDF files. Install it: pip install pdfplumber") from e

        texts: List[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return _clean_whitespace("\n\n".join(texts))

    elif suffix in (".docx", ".doc"):
        try:
            from docx import Document
        except Exception as e:
            raise RuntimeError("python-docx is required to parse DOCX files. Install it: pip install python-docx") from e

        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return _clean_whitespace("\n\n".join(paragraphs))

    else:
        raise ValueError("Unsupported file type. Supported: .pdf, .docx, .doc")


def prepare_prompt(text: str, instruction: Optional[str] = None, max_chars: int = 3000) -> str:
    """Prepare a single prompt string combining an optional instruction and the document text.

    This will truncate the document text to `max_chars` characters (preserving start and end
    if possible) to keep prompts within model limits.
    """
    cleaned = _clean_whitespace(text)
    if len(cleaned) <= max_chars:
        doc_part = cleaned
    else:
        # keep start and end with ellipsis in the middle
        keep = max_chars // 2
        start = cleaned[:keep]
        end = cleaned[-keep:]
        doc_part = start + "\n\n[...trimmed...]\n\n" + end

    if instruction:
        prompt = f"{instruction}\n\nDocument:\n{doc_part}"
    else:
        prompt = f"Document:\n{doc_part}"
    return prompt


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parsers/doc_parse.py <file.pdf|file.docx>")
        raise SystemExit(1)

    fp = sys.argv[1]
    try:
        txt = extract_text(fp)
        print("---EXTRACTED TEXT START---")
        print(txt[:4000])
        print("---EXTRACTED TEXT END---")
    except Exception as e:
        print("Error:", e)


