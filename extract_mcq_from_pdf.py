import json
import re
from pathlib import Path

TXT_PATH = Path("Preguntas P2.txt")
OUTPUT_PATH = Path("mcq_from_txt.json")

num_re = re.compile(r"^(\d+)\.\s*(.*)")


def load_lines(path: Path):
    """Lee el TXT y devuelve una lista de líneas sin blancos."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = [l.strip() for l in text.splitlines()]
    return [l for l in lines if l]


def parse_question(lines, start_idx, q_number):
    """
    Parsea UNA pregunta que empieza en start_idx:

    TÍTULO
    1.
    texto opción 1
    2.
    texto opción 2
    3. texto opción 3
    4.
    texto opción 4
    """
    title = lines[start_idx]
    i = start_idx + 1
    options = []
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    n = len(lines)

    while i < n:
        m = num_re.match(lines[i])
        if not m:
            break  # se terminó el bloque de opciones

        num = int(m.group(1))
        rest = m.group(2).strip()

        text_parts = []
        if rest:
            text_parts.append(rest)

        j = i + 1
        while j < n:
            nxt = lines[j]
            m_next = num_re.match(nxt)
            if m_next:
                # siguiente opción (2., 3., 4., etc.)
                break

            # mirar si esta línea es encabezado de la próxima pregunta:
            # línea no numerada, y la siguiente es "1."
            if j + 1 < n:
                m_after = num_re.match(lines[j + 1])
                if m_after and int(m_after.group(1)) == 1:
                    # nxt es encabezado de la próxima pregunta
                    break

            text_parts.append(nxt)
            j += 1

        option_text = " ".join(text_parts).strip()
        label = labels[num - 1] if num - 1 < len(labels) else "?"

        options.append({"label": label, "text": option_text})
        i = j

    question = {
        "number": q_number,
        "question": title,
        "options": options,
        "correct": "A",      # por defecto, después las corregís vos
        "explanation": ""
    }
    return question, i


def parse_all(lines):
    """
    Recorre todas las líneas del TXT y arma la lista de preguntas.
    Una pregunta arranca cuando hay:

    LÍNEA NO NUMERADA
    seguida de
    "1." en la línea siguiente.
    """
    questions = []
    i = 0
    qn = 1
    n = len(lines)

    while i < n - 1:
        m = num_re.match(lines[i])

        # inicio de pregunta: línea NO numerada + siguiente línea "1."
        if not m and i + 1 < n:
            m_next = num_re.match(lines[i + 1])
            if m_next and int(m_next.group(1)) == 1:
                q, new_i = parse_question(lines, i, qn)
                questions.append(q)
                qn += 1
                i = new_i
                continue

        i += 1

    return questions


def main():
    if not TXT_PATH.exists():
        print(f"No se encontró el TXT: {TXT_PATH}")
        return

    print(f"Leyendo TXT: {TXT_PATH}")
    lines = load_lines(TXT_PATH)

    print("Parseando preguntas...")
    questions = parse_all(lines)

    print(f"Preguntas detectadas: {len(questions)}")

    data = [{
        "pdf_name": "Preguntas P2.pdf",
        "chunk_id": 0,
        "questions": questions
    }]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Listo. JSON guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
