import json
import re
from pathlib import Path

import fitz  # PyMuPDF

PDF_PATH = Path("Preguntas P2.pdf")
OUTPUT_PATH = Path("mcq_from_pdf.json")


def extract_text(pdf_path: Path) -> list[str]:
    """Devuelve una lista de líneas limpias de todo el PDF."""
    doc = fitz.open(pdf_path)
    lines: list[str] = []
    for page in doc:
        txt = page.get_text()
        for raw_line in txt.split("\n"):
            line = raw_line.strip()
            if line:
                lines.append(line)
    return lines


def parse_blocks_as_mcq(lines: list[str]):
    """
    Interpreta el PDF como bloques del tipo:

    TÍTULO DEL TEMA:
    1. opción 1
    2. opción 2
    3. opción 3
    4. opción 4

    Cada bloque (1–4) se convierte en UNA pregunta,
    usando el título previo como enunciado.

    Si aparece texto como:
      - 'Mosto y derivados vínicos:'
      - 'El aglomerado y el MDF:'
    lo tomamos como título/encabezado.
    """

    questions = []
    current_title = None
    current_options: list[str] = []
    question_number = 1

    num_re = re.compile(r"^(\d+)\.\s*(.*)")

    for line in lines:
        # ¿Es una línea numerada tipo "1. ..."?
        m_num = num_re.match(line)
        if m_num:
            num = int(m_num.group(1))
            text = m_num.group(2).strip()

            # Si empezamos un nuevo bloque con "1.", reiniciamos opciones
            if num == 1 and current_options:
                # Si había opciones colgadas (por seguridad, por si no eran 4 exactas)
                if len(current_options) == 4:
                    questions.append(
                        build_question(
                            question_number,
                            current_title,
                            current_options
                        )
                    )
                    question_number += 1
                # Reiniciamos el bloque de opciones
                current_options = []

            # Agregamos la opción (1,2,3,4)
            # aunque el número no lo usamos directamente,
            # el orden define A,B,C,D
            current_options.append(text)

            # Si ya tenemos 4 opciones, cerramos un bloque de pregunta
            if len(current_options) == 4:
                questions.append(
                    build_question(
                        question_number,
                        current_title,
                        current_options
                    )
                )
                question_number += 1
                current_options = []

            continue

        # Si NO es una línea numerada, puede ser:
        # - Título de tema (termina en ":" o está en mayúsculas)
        # - Consigna tipo "El aglomerado y el MDF:"
        # Lo usamos como "enunciado" base para las siguientes 1–4.
        # Si no querés títulos muy genéricos, podés ajustar este heurístico.
        if (
            line.endswith(":")
            or line.istitle()
            or line.isupper()
        ):
            current_title = line
            continue

        # Si es otro texto (instrucciones tipo "Haga un diagrama..."), lo ignoramos
        # porque no forman multiple choice.


    # Por si al final quedó un bloque incompleto con opciones
    if current_options:
        if len(current_options) == 4:
            questions.append(
                build_question(
                    question_number,
                    current_title,
                    current_options
                )
            )

    return questions


def build_question(q_number: int, title: str | None, options_texts: list[str]) -> dict:
    """
    Construye el diccionario de pregunta en el formato que usa tu proyecto.

    - title: encabezado del tema (puede ser None)
    - options_texts: lista de 4 strings → A,B,C,D
    """
    if len(options_texts) != 4:
        # Seguridad: rellenar o recortar por si algo raro pasa
        options_texts = (options_texts + [""] * 4)[:4]

    # Enunciado de la pregunta: si hay título, lo usamos;
    # si no, ponemos algo genérico.
    if title:
        question_text = title
    else:
        question_text = "Seleccione la opción correcta según el enunciado."

    option_labels = ["A", "B", "C", "D"]
    options = [
        {"label": label, "text": text}
        for label, text in zip(option_labels, options_texts)
    ]

    return {
        "number": q_number,
        "question": question_text,
        "options": options,
        "correct": "A",      # por defecto, después las corregís vos
        "explanation": ""
    }


def main():
    if not PDF_PATH.exists():
        print(f"No se encontró el PDF: {PDF_PATH}")
        return

    print("Leyendo PDF y extrayendo líneas...")
    lines = extract_text(PDF_PATH)

    print("Parseando bloques 1–4 como preguntas...")
    questions = parse_blocks_as_mcq(lines)

    print(f"Preguntas detectadas: {len(questions)}")

    data = [
        {
            "pdf_name": PDF_PATH.name,
            "chunk_id": 0,
            "questions": questions,
        }
    ]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Listo. JSON guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
