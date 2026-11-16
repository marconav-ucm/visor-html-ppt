---
name: llm-anonimo
description: Úsala siempre que vayas a mandar una petición a un LLM externo gratuito (FreeLLMAPI o cualquiera de sus proveedores) o a un modelo local con Ollama. Clasifica antes el riesgo de datos de la tarea (verde, ámbar, rojo), decide si va a FreeLLMAPI, a Ollama local o a ninguno, anonimiza el contenido con scripts/anonimizar.py y envía con scripts/enviar.py sin cabeceras ni metadatos que identifiquen al usuario.
---

# LLM anónimo: FreeLLMAPI y Ollama

FreeLLMAPI es un proxy que reenvía cada petición a proveedores con capa gratuita (Groq, Gemini, Mistral, OpenRouter, Cerebras y otros). Esos proveedores pueden guardar y usar para entrenamiento lo que reciben en el plan gratuito. Por tanto, todo lo que salga hacia FreeLLMAPI se trata como si se publicara. Ollama corre en el Mac del usuario y nada sale del equipo.

Objetivo doble: no exponer datos personales y no gastar tokens de Claude en tareas mecánicas que puede hacer un modelo gratuito o local.

## 1. Clasificar la tarea ANTES de enviar nada

| Nivel | Qué contiene | Destino |
|---|---|---|
| VERDE | Nada personal ni inédito: HTML o CSS de una diapositiva del Neumann, código genérico, resumir un capítulo de un libro publicado, traducir texto docente sin nombres, generar preguntas tipo test de un tema | FreeLLMAPI tras pasar `anonimizar.py --comprobar` |
| ÁMBAR | Datos personales que se pueden quitar sin perder la tarea: manuscrito con nombres de autores y afiliaciones, correo con firma, rúbrica con nombres de alumnos, carta de revisores | Anonimizar con `anonimizar.py`, revisar el texto que sale, enviar a FreeLLMAPI y reidentificar en local con `--restaurar`. Si la tarea no tiene sentido sin los datos, pasa a ROJO |
| ROJO | Datos de salud de personas identificables o identificables por combinación (edad + sexo + diagnóstico + fecha + centro), bases de datos de pacientes, participantes o alumnos, notas, datos brutos de un ensayo no publicado, manuscrito inédito bajo revisión de otra persona, credenciales, claves de API | Nunca a FreeLLMAPI. Solo Ollama local, o Claude si el usuario lo decide. Una base de datos con datos personales es ROJO aunque se quiten los nombres: la seudonimización no anonimiza (RGPD, considerando 26) |

Reglas de decisión:
- En caso de duda, sube un nivel.
- Datos de salud son categoría especial (RGPD art. 9). Un conjunto de datos de pacientes o participantes siempre es ROJO.
- Un manuscrito inédito propio es ÁMBAR: quitar autores, centro, financiación y números de registro y comité ético. Uno ajeno en revisión por pares es ROJO (confidencialidad editorial).
- Si la tarea es importante o delicada (redacción final, respuesta a revisores, análisis estadístico definitivo), no se delega: se hace con Claude y las skills del usuario. El LLM gratuito es para borradores, código repetitivo, formateo, traducciones de apoyo y tareas mecánicas.

Antes de enviar, di al usuario en una línea: nivel asignado, motivo y destino. En ROJO, pide confirmación si el usuario había pedido FreeLLMAPI.

## 2. Anonimizar

```bash
python3 scripts/anonimizar.py entrada.txt -o salida_anon.txt -m mapa.json [-n nombres.txt]
python3 scripts/anonimizar.py salida_anon.txt --comprobar      # sale con código 1 si queda algo
python3 scripts/anonimizar.py respuesta.txt --restaurar -m mapa.json -o respuesta_final.txt
```

- Sustituye por marcadores (`[EMAIL_1]`, `[TEL_1]`, `[DNI_1]`, `[PERSONA_2]`...): correos, teléfonos, DNI/NIE, IBAN, fechas, números de historia clínica, URL, IP, rutas de archivo con nombre de usuario, ORCID, DOI de trabajos propios si se pide, y los nombres, centros y proyectos que haya en `nombres.txt` (uno por línea).
- `nombres.txt` vive fuera del repositorio. Incluye por defecto el nombre del usuario, su correo institucional, la universidad y los nombres de coautores y alumnos que aparezcan.
- `mapa.json` nunca se envía ni se sube a git. Bórralo al terminar.
- Los regex no detectan todos los nombres propios. Lee siempre el texto anonimizado antes de enviarlo y busca nombres, lugares y fechas sueltos. Para ÁMBAR largo, se puede pedir antes a Ollama local que liste nombres propios del texto y añadirlos a `nombres.txt`.
- Archivos .docx, .pptx o .pdf: extraer solo el texto. No enviar el archivo, porque sus metadatos llevan autor, organización y rutas.

## 3. Enviar sin identificar al usuario

```bash
python3 scripts/enviar.py --destino freellmapi --nivel verde  -p prompt_anon.txt [-s sistema.txt] [--modelo auto]
python3 scripts/enviar.py --destino ollama     --nivel rojo   -p prompt.txt --modelo qwen3:8b
```

`enviar.py`:
- Lee la URL de `FREELLMAPI_URL` (por defecto `http://localhost:3001/v1`, ajustar a lo que muestre el panel de FreeLLMAPI) y la clave de `FREELLMAPI_KEY`. Ollama: `OLLAMA_URL`, por defecto `http://localhost:11434/v1`.
- Rechaza `--nivel rojo` hacia FreeLLMAPI y aborta si `--comprobar` encuentra datos residuales.
- Manda solo `model`, `messages` y `temperature`. Sin campo `user`, sin metadatos, con `User-Agent: llm-client`.
- No guarda historial. Cada petición es independiente: no arrastrar contexto de peticiones anteriores.

Higiene del prompt:
- No firmar ni presentarse («soy profesor de la UCM...»). Describir la tarea en abstracto.
- No pegar rutas, nombres de archivo con nombres propios ni enlaces a repositorios o drives privados.
- Para el HTML del Neumann y similares basta el contenido técnico, sin el nombre de la asignatura ni del grupo.

## 4. Límites que hay que decir al usuario

- El contenido va anónimo, pero cada proveedor ve la clave de API con la que FreeLLMAPI llama, y esa clave está asociada a una cuenta. Las cuentas de los proveedores deben crearse con un correo que no sea el institucional.
- FreeLLMAPI es un proyecto de terceros para uso personal y experimental. Instalar solo desde el repositorio oficial `tashfeenahmed/freellmapi` y revisar el commit. Hay copias y bifurcaciones con nombre parecido.
- La calidad de los modelos gratuitos y locales es menor que la de Claude. Revisar siempre lo que devuelven antes de usarlo.

## 5. Ollama en el Mac

Instalación (una vez):
1. Descargar Ollama para macOS desde ollama.com o `brew install ollama`.
2. Abrir la app. Queda escuchando en `http://localhost:11434`.
3. Descargar un modelo según la memoria del Mac: 8 GB → `ollama pull gemma3:4b`. 16 GB → `ollama pull qwen3:8b`. 32 GB o más → `ollama pull qwen3:14b` o `gemma3:27b`. Comprobar con `ollama run qwen3:8b "hola"`.
4. Para que Claude Code en la nube lo use, el Mac tiene que estar conectado a la sesión (Remote Control) o hay que lanzar `enviar.py` desde el propio Mac. Una sesión en la nube no ve `localhost` del Mac.

Ollama no gasta tokens ni manda nada fuera, así que es el destino por defecto para ÁMBAR y ROJO cuando la tarea es mecánica (extraer, reformatear, clasificar texto, listar nombres propios para anonimizar).
