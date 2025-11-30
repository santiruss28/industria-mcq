import json
import re
from pathlib import Path

TXT_PATH = Path("Preguntas P2.txt")
OUTPUT_PATH = Path("mcq_from_txt.json")


def load_lines(path: Path):
    """Lee el TXT y devuelve una lista de líneas sin blancos."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # Normalizar saltos y limpiar
    lines = [l.strip() for l in text.splitlines()]
    # Quitamos líneas completamente vacías
    return [l for l in lines if l]


num_re = re.compile(r"^(\d+)\.\s*(.*)")


def parse_questions(lines):
    """
    Reglas:
    - Cualquier línea NO numerada se toma como posible 'encabezado'.
      El encabezado vigente se usará como 'question' cuando aparezca un bloque 1..n.
    - Un bloque de opciones comienza cuando aparece '1.'.
    - Mientras haya líneas numeradas 1., 2., 3., 4. (5. etc) seguimos agregando opciones.
    - Cuando vuelve a aparecer un '1.' o termina el archivo, cerramos la pregunta.
    - Las opciones pueden estar como:
        '1.' (línea siguiente = texto)
        '1. texto...' (todo en una línea)
      y pueden tener continuaciones en varias líneas.
    """

    questions = []
    current_title = None      # último encabezado leído
    in_options = False
    current_options = []      # lista de textos de opciones en el bloque actual
    current_option_index = None
    q_number = 1

    def flush_question():
        nonlocal q_number, current_options
        if not current_options:
            return
        # Asignar labels A, B, C, D, E,... según cantidad de opciones
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        options_struct = []
        for i, text in enumerate(current_options):
            label = labels[i]
            options_struct.append({"label": label, "text": text.strip()})

        question_text = current_title or "Seleccione la opción correcta."

        questions.append({
            "number": q_number,
            "question": question_text,
            "options": options_struct,
            "correct": "A",      # por defecto
            "explanation": ""
        })
        q_number += 1
        current_options = []

    for line in lines:
        m = num_re.match(line)

        if m:
            # Línea numerada tipo "1." o "1. texto"
            num = int(m.group(1))
            rest = m.group(2).strip()

            # Si aparece un 1. y ya estábamos en un bloque de opciones,
            # cerramos la pregunta anterior y arrancamos una nueva.
            if num == 1 and in_options and current_options:
                flush_question()

            # Entramos (o seguimos) modo opciones
            in_options = True
            current_option_index = num  # 1, 2, 3, ...

            # Asegurar longitud de lista de opciones
            while len(current_options) < num:
                current_options.append("")

            # Si hay texto en la misma línea, lo ponemos; si no, se completará
            # con las siguientes líneas no numeradas.
            if rest:
                current_options[num - 1] = (
                    current_options[num - 1] + " " + rest
                ).strip()

        else:
            # NO es una línea numerada
            if in_options:
                # Estamos dentro de un bloque de opciones:
                # esto es continuación de la última opción.
                if current_option_index is not None and current_options:
                    idx = current_option_index - 1
                    current_options[idx] = (
                        current_options[idx] + " " + line
                    ).strip()
            else:
                # No estamos en opciones → actualizar encabezado
                current_title = line

    # Fin del archivo: cerrar último bloque si había
    if in_options and current_options:
        flush_question()

    return questions


def main():
    if not TXT_PATH.exists():
        print(f"No se encontró el TXT: {TXT_PATH}")
        return

    print(f"Leyendo TXT: {TXT_PATH}")
    lines = load_lines(TXT_PATH)

    print("Parseando preguntas...")
    questions = parse_questions(lines)

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
