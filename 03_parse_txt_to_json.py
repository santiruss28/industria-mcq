import json
from pathlib import Path
import re

DATA_DIR = Path("data")
TXT_PATH = DATA_DIR / "mcq_simple.txt"
JSON_PATH = DATA_DIR / "mcq.json"


def parse_file():
    if not TXT_PATH.exists():
        print(f"No se encontró {TXT_PATH}")
        return

    chunks = []
    current_chunk = None
    current_question = None

    def flush_question():
        nonlocal current_question
        if current_question is not None:
            # Limpiamos espacios
            current_question["question"] = current_question["question"].strip()
            current_question["explanation"] = current_question["explanation"].strip()
            for opt in current_question["options"]:
                opt["text"] = opt["text"].strip()
            current_chunk["questions"].append(current_question)
            current_question = None

    with open(TXT_PATH, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            # Nuevo chunk
            if line.startswith("====="):
                # Ej: ===== 13-Industria Metalmecánica.pdf | CHUNK 0 =====
                flush_question()
                if current_chunk is not None:
                    chunks.append(current_chunk)

                m = re.match(r"^===== (.+?) \| CHUNK (\d+) =====", line.strip())
                if not m:
                    continue
                pdf_name = m.group(1)
                chunk_id = int(m.group(2))
                current_chunk = {
                    "pdf_name": pdf_name,
                    "chunk_id": chunk_id,
                    "questions": []
                }
                current_question = None
                continue

            if current_chunk is None:
                continue  # todavía no empezamos un bloque válido

            # Nueva pregunta
            m_q = re.match(r"^PREGUNTA\s+(\d+):\s*(.*)$", line)
            if m_q:
                flush_question()
                num = int(m_q.group(1))
                qtext = m_q.group(2)
                current_question = {
                    "number": num,
                    "question": qtext,
                    "options": [],
                    "correct": None,
                    "explanation": ""
                }
                continue

            # Opciones A/B/C/D
            m_opt = re.match(r"^([ABCD])\)\s*(.*)$", line)
            if m_opt and current_question is not None:
                label = m_opt.group(1)
                text = m_opt.group(2)
                current_question["options"].append({
                    "label": label,
                    "text": text
                })
                continue

            # Respuesta correcta
            m_ans = re.match(r"^RESPUESTA CORRECTA:\s*([ABCD])", line)
            if m_ans and current_question is not None:
                current_question["correct"] = m_ans.group(1)
                continue

            # Explicación
            m_exp = re.match(r"^EXPLICACIÓN:\s*(.*)$", line)
            if m_exp and current_question is not None:
                current_question["explanation"] = m_exp.group(1)
                continue

            # Texto extra (por si la explicación ocupa varias líneas)
            if current_question is not None and current_question["explanation"]:
                # Si no es línea vacía ni nueva pregunta, se suma a la explicación
                if line.strip() and not line.startswith("PREGUNTA ") and not line.startswith("====="):
                    current_question["explanation"] += " " + line.strip()

        # Final del archivo
        flush_question()
        if current_chunk is not None:
            chunks.append(current_chunk)

    # Guardamos JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f_out:
        json.dump(chunks, f_out, ensure_ascii=False, indent=2)

    print(f"Listo. JSON generado en {JSON_PATH}")
    print(f"Chunks parseados: {len(chunks)}")


if __name__ == "__main__":
    parse_file()
