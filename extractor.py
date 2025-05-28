import re

def extraer_datos_ocr(texto: str) -> dict:
    match = re.search(r"C[oó]digo[:;\s]*([0-9]+)", texto, re.IGNORECASE)
    codigo = match.group(1) if match else None

    dni_match = re.search(r"DNI[:;\s]*([0-9]+)", texto, re.IGNORECASE)

    apellidos_match = re.search(
        r"Apellidos.*?\n(?:\d+\n)?([A-ZÁÉÍÓÚÑ]+)\n(?:\d+\n)?([A-ZÁÉÍÓÚÑ]+)", texto, re.IGNORECASE
    )
    apellido_completo = f"{apellidos_match.group(1)} {apellidos_match.group(2)}" if apellidos_match else None

    nombres_match = re.search(
        r"Nombres.*?\n(?:\d+\n)?([A-ZÁÉÍÓÚÑ]+(?: [A-ZÁÉÍÓÚÑ]+)*)", texto, re.IGNORECASE
    )

    facultad_match = re.search(
        r"Fac[uú]l{1,3}[ti1l]?[aá]?d[:;\s]*\n?([A-ZÁÉÍÓÚÑa-záéíóúñ ]+)", texto, re.IGNORECASE
    )

    carrera_match = re.search(
        r"Carr{1,2}e?ra[:;\s]*\n?([A-ZÁÉÍÓÚÑ. \-]+)", texto, re.IGNORECASE
    )

    return {
        "Codigo": codigo,
        "DNI": dni_match.group(1) if dni_match else None,
        "Apellidos": apellido_completo,
        "Nombres": nombres_match.group(1).strip() if nombres_match else None,
        "Facultad": facultad_match.group(1).strip() if facultad_match else None,
        "Carrera": carrera_match.group(1).strip() if carrera_match else None,
    }
