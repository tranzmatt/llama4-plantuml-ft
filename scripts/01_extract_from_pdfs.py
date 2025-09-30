# 01_extract_from_pdfs.py
import re, json, sys, pathlib
import fitz  # pymupdf
from tqdm import tqdm

RAW_DIR = pathlib.Path("data/raw")
OUT_TXT = pathlib.Path("data/extracted/corpus.txt")
OUT_SAMPLES = pathlib.Path("data/extracted/plantuml_samples.jsonl")
OUT_TXT.parent.mkdir(parents=True, exist_ok=True)

uml_block_re = re.compile(r"@startuml.*?@enduml", re.DOTALL | re.IGNORECASE)

def extract_text(pdf_path: pathlib.Path) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for p in doc:
        # simple text pull; pymupdf keeps layout decently
        pages.append(p.get_text("text"))
    return "\n\n".join(pages)

def harvest_samples(text: str):
    samples = []
    for m in uml_block_re.finditer(text):
        code = m.group(0).strip()
        # grab 5 lines above and below as crude "context"
        start, end = m.span()
        pre = text[:start].splitlines()
        post = text[end:].splitlines()
        context = "\n".join(pre[-5:] + ["[...code omitted here...]",] + post[:5]).strip()
        samples.append({"context": context, "plantuml": code})
    return samples

def main():
    all_text = []
    all_samples = []
    for pdf in RAW_DIR.glob("*.pdf"):
        txt = extract_text(pdf)
        all_text.append(f"===== {pdf.name} =====\n{txt}")
        all_samples.extend(harvest_samples(txt))
    OUT_TXT.write_text("\n\n".join(all_text), encoding="utf-8")
    with OUT_SAMPLES.open("w", encoding="utf-8") as f:
        for s in all_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT_TXT} and {OUT_SAMPLES} with {len(all_samples)} samples")

if __name__ == "__main__":
    sys.exit(main())

