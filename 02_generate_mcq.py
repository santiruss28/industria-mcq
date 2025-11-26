import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = Path("data")
CHUNKS_PATH = DATA_DIR / "chunks.jsonl"
OUT_PATH = DATA_DIR / "mcq_simple.txt"

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = """
Eres un profesor universitario experto en la materia y en evaluación.
Vas a generar preguntas de opción múltiple de ALTA dificultad
a partir de fragmentos de texto de apuntes.

Reglas:
- 4 opciones por pregunta: A, B, C, D.
- Solo una es correcta.
- Distractores plausibles (técnicamente creíbles).
- Nivel alto: análisis, aplicación, razonamiento.
- NO hagas preguntas triviales de memoria literal.
- Las opciones deben ser completas, no respuestas de una palabra suelta.
"""

USER_TEMPLATE = """
Generá entre 4 y 6 preguntas de opción múltiple de ALTA dificultad
a partir del siguiente texto:

\"\"\"{chunk_text}\"\"\"

Formato de salida (IMPORTANTE, seguí EXACTAMENTE este formato):

PREGUNTA 1: enunciado de la pregunta...
A) opción A
B) opción B
C) opción C
D) opción D
RESPUESTA CORRECTA: X
EXPLICACIÓN: explicación breve de por qué esa opción es correcta.

PREGUNTA 2: ...
A) ...
B) ...
C) ...
D) ...
RESPUESTA CORRECTA: X
EXPLICACIÓN: ...

(Usá este mismo patrón para todas las preguntas. No agregues texto fuera de este esquema.)
"""


def call_model(chunk_text: str) -> str:
    """Llama al modelo y devuelve las preguntas como texto plano."""
    user_prompt = USER_TEMPLATE.format(chunk_text=chunk_text)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def main():
    if not CHUNKS_PATH.exists():
        print("No se encontró data/chunks.jsonl. Corré primero 01_extract_chunks.py")
        return

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f_in, \
         open(OUT_PATH, "w", encoding="utf-8") as f_out:

        for line in tqdm(f_in, desc="Generando MCQ (simple)"):
            record = json.loads(line)
            text = record["text"]

            header = f"\n===== {record['pdf_name']} | CHUNK {record['chunk_id']} =====\n"
            f_out.write(header)

            try:
                questions_block = call_model(text)
            except Exception as e:
                f_out.write(f"[ERROR EN ESTE CHUNK: {e}]\n")
                time.sleep(2)
                continue

            f_out.write(questions_block)
            f_out.write("\n\n")

    print(f"\nListo. Preguntas generadas en: {OUT_PATH}")


if __name__ == "__main__":
    main()
