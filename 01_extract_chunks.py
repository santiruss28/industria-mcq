import os
import json
from pathlib import Path

import fitz  # pymupdf
from tqdm import tqdm

# === RUTAS ROBUSTAS: SIEMPRE RELATIVAS AL ARCHIVO .PY ===
BASE_DIR = Path(__file__).resolve().parent

PDF_DIR = BASE_DIR / "pdfs"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_PATH = DATA_DIR / "chunks.jsonl"

# Ajustá estos valores si querés chunks más largos/cortos
CHARS_PER_CHUNK = 2000
CHARS_OVERLAP = 200


def clean_text(text: str) -> str:
    """Limpieza básica del texto extraído."""
    text = text.replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    text = " ".join([l for l in lines if l])
    return text


def chunk_text(text: str, max_chars: int, overlap: int):
    """Divide el texto en chunks solapados."""
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if len(chunk) > 0:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap

    return chunks


def extract_pdf_text(pdf_path: Path) -> str:
    """Extrae texto de un PDF y lo limpia."""
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return clean_text("\n".join(texts))


def extract_txt_text(txt_path: Path) -> str:
    """Lee un .txt y lo limpia."""
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    return clean_text(text)


def main():
    print(f"Directorio base: {BASE_DIR}")
    print(f"Archivo de salida: {CHUNKS_PATH}")

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    txt_files = sorted(PDF_DIR.glob("*.txt"))

    if not pdf_files and not txt_files:
        print(f"No se encontraron PDFs ni TXT en la carpeta: {PDF_DIR}")
        return

    total_docs = len(pdf_files) + len(txt_files)
    print(f"Documentos a procesar: {total_docs} (PDF: {len(pdf_files)}, TXT: {len(txt_files)})")

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f_out:
        # Procesar PDFs
        for pdf_path in tqdm(pdf_files, desc="Procesando PDFs"):
            raw_text = extract_pdf_text(pdf_path)
            chunks = chunk_text(raw_text, CHARS_PER_CHUNK, CHARS_OVERLAP)

            for i, chunk in enumerate(chunks):
                record = {
                    "pdf_name": pdf_path.name,  # mantenemos la misma clave por compatibilidad
                    "chunk_id": i,
                    "text": chunk,
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Procesar TXT
        for txt_path in tqdm(txt_files, desc="Procesando TXT"):
            raw_text = extract_txt_text(txt_path)
            chunks = chunk_text(raw_text, CHARS_PER_CHUNK, CHARS_OVERLAP)

            for i, chunk in enumerate(chunks):
                record = {
                    "pdf_name": txt_path.name,  # igual clave, aunque sea txt
                    "chunk_id": i,
                    "text": chunk,
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Listo. Chunks guardados en: {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
