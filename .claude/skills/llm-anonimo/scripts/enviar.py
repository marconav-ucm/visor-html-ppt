#!/usr/bin/env python3
"""Envía una petición anónima a FreeLLMAPI o a Ollama local (API compatible con OpenAI).

Uso:
  enviar.py --destino freellmapi --nivel verde -p prompt.txt [-s sistema.txt] [--modelo auto]
  enviar.py --destino ollama --nivel rojo -p prompt.txt --modelo qwen3:8b

Variables: FREELLMAPI_URL, FREELLMAPI_KEY, OLLAMA_URL
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from anonimizar import cargar_nombres, comprobar  # noqa: E402

DESTINOS = {
    "freellmapi": (os.environ.get("FREELLMAPI_URL", "http://localhost:3001/v1"),
                   os.environ.get("FREELLMAPI_KEY", "")),
    "ollama": (os.environ.get("OLLAMA_URL", "http://localhost:11434/v1"), "ollama"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", choices=DESTINOS, required=True)
    ap.add_argument("--nivel", choices=["verde", "ambar", "rojo"], required=True)
    ap.add_argument("-p", "--prompt", required=True)
    ap.add_argument("-s", "--sistema")
    ap.add_argument("-n", "--nombres")
    ap.add_argument("--modelo", default="auto")
    ap.add_argument("--temperatura", type=float, default=0.3)
    ap.add_argument("-o", "--salida")
    a = ap.parse_args()

    if a.destino == "freellmapi" and a.nivel == "rojo":
        sys.exit("BLOQUEADO: nivel rojo no puede salir a FreeLLMAPI. Usa --destino ollama.")

    prompt = Path(a.prompt).read_text(encoding="utf-8")
    sistema = Path(a.sistema).read_text(encoding="utf-8") if a.sistema else ""

    if a.destino == "freellmapi":
        h = comprobar(sistema + "\n" + prompt, cargar_nombres(a.nombres))
        if h:
            for tipo, valor in h:
                print(f"RESIDUAL {tipo}: {valor}", file=sys.stderr)
            sys.exit("BLOQUEADO: quedan datos identificativos. Pasa antes anonimizar.py.")

    mensajes = ([{"role": "system", "content": sistema}] if sistema else []) + \
               [{"role": "user", "content": prompt}]
    cuerpo = json.dumps({"model": a.modelo, "messages": mensajes,
                         "temperature": a.temperatura}).encode()

    url, clave = DESTINOS[a.destino]
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=cuerpo, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "llm-client")
    if clave:
        req.add_header("Authorization", f"Bearer {clave}")

    with urllib.request.urlopen(req, timeout=300) as r:
        datos = json.load(r)
    texto = datos["choices"][0]["message"]["content"]
    print(f"[{a.destino} · modelo {datos.get('model', a.modelo)}]", file=sys.stderr)

    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    else:
        print(texto)


if __name__ == "__main__":
    main()
