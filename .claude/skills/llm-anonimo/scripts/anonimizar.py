#!/usr/bin/env python3
"""Anonimiza un texto antes de mandarlo a un LLM externo y lo reidentifica después.

Uso:
  anonimizar.py entrada.txt -o salida.txt -m mapa.json [-n nombres.txt]
  anonimizar.py salida.txt --comprobar
  anonimizar.py respuesta.txt --restaurar -m mapa.json -o final.txt
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Orden importa: lo más específico primero.
PATRONES = [
    ("EMAIL", r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    ("URL", r"https?://[^\s<>\"')]+|www\.[^\s<>\"')]+"),
    ("IBAN", r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){4,7}\b"),
    ("ORCID", r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b"),
    ("DNI", r"\b[XYZ]?\d{7,8}[-\s]?[A-HJ-NP-TV-Z]\b"),
    ("IP", r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ("TEL", r"(?<![\w-])(?:\+\d{1,3}[\s.-]?)?(?:[6-9]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}|[6-9]\d[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2})(?![\w-])"),
    ("NHC", r"(?i)\b(?:NHC|n[ºo°]\s*(?:de\s*)?historia(?:\s*cl[ií]nica)?|historia\s*cl[ií]nica|SIP|CIP|NUSS|tarjeta\s*sanitaria)\s*[:#nº°]*\s*[A-Z0-9-]{4,}"),
    ("FECHA", r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b"),
    ("RUTA", r"(?:/Users|/home|C:\\Users)[/\\][^\s\"']+"),
]

RESIDUALES = PATRONES


def cargar_nombres(ruta):
    if not ruta:
        return []
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    nombres = [l.strip() for l in lineas if l.strip() and not l.startswith("#")]
    return sorted(set(nombres), key=len, reverse=True)


def anonimizar(texto, nombres):
    mapa = {}
    inverso = {}
    contadores = {}

    def marcador(tipo, valor):
        clave = valor.strip()
        if clave in inverso:
            return inverso[clave]
        contadores[tipo] = contadores.get(tipo, 0) + 1
        m = f"[{tipo}_{contadores[tipo]}]"
        mapa[m] = clave
        inverso[clave] = m
        return m

    for nombre in nombres:
        patron = re.compile(r"(?<!\w)" + re.escape(nombre) + r"(?!\w)", re.IGNORECASE)
        texto = patron.sub(lambda mt: marcador("PERSONA", mt.group(0)), texto)

    for tipo, patron in PATRONES:
        texto = re.sub(patron, lambda mt, t=tipo: marcador(t, mt.group(0)), texto)
    return texto, mapa


def comprobar(texto, nombres):
    hallazgos = []
    for tipo, patron in RESIDUALES:
        for mt in re.finditer(patron, texto):
            hallazgos.append((tipo, mt.group(0)))
    for nombre in nombres:
        if re.search(r"(?<!\w)" + re.escape(nombre) + r"(?!\w)", texto, re.IGNORECASE):
            hallazgos.append(("PERSONA", nombre))
    return hallazgos


def restaurar(texto, mapa):
    for m in sorted(mapa, key=len, reverse=True):
        texto = texto.replace(m, mapa[m])
    return texto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida")
    ap.add_argument("-m", "--mapa")
    ap.add_argument("-n", "--nombres", help="archivo con nombres, centros o proyectos, uno por línea")
    ap.add_argument("--comprobar", action="store_true")
    ap.add_argument("--restaurar", action="store_true")
    a = ap.parse_args()

    texto = Path(a.entrada).read_text(encoding="utf-8")
    nombres = cargar_nombres(a.nombres)

    if a.comprobar:
        h = comprobar(texto, nombres)
        if h:
            for tipo, valor in h:
                print(f"RESIDUAL {tipo}: {valor}", file=sys.stderr)
            sys.exit(1)
        print("OK: sin datos identificativos detectados (revisa igualmente nombres propios a mano)")
        return

    if a.restaurar:
        if not a.mapa:
            sys.exit("Falta -m mapa.json")
        mapa = json.loads(Path(a.mapa).read_text(encoding="utf-8"))
        salida = restaurar(texto, mapa)
    else:
        salida, mapa = anonimizar(texto, nombres)
        if a.mapa:
            Path(a.mapa).write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(mapa)} elementos sustituidos", file=sys.stderr)

    if a.salida:
        Path(a.salida).write_text(salida, encoding="utf-8")
    else:
        sys.stdout.write(salida)


if __name__ == "__main__":
    main()
