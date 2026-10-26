# Obtener únicamente los prompts

El flujo principal extrae los enunciados de TACO que ya existen en
`modeling/data/raw/TACO/{train,test}/*.arrow`. No requiere Ollama, modelos,
soluciones de referencia, casos de prueba, auditorías ni `candidate_ids.csv`.

Desde la raíz del repositorio:

```bash
.venv/bin/python -m pip install -r modeling/requirements-prompts.txt
.venv/bin/python -m modeling.src.data.extract_prompts
```

El resultado está en `modeling/data/processed/prompts.jsonl`, con exactamente
un campo por registro:

```json
{"prompt": "Enunciado original del problema..."}
```

JSONL conserva cada enunciado completo en una línea JSON; los saltos de línea
internos se representan como `\n`. Se conserva el texto original, incluidos
los ejemplos del enunciado. No se exportan soluciones, tests privados,
metadatos ni código inicial. No se llama a ningún servicio externo.

Por defecto se recorren primero train y después test, se omiten textos vacíos
y se eliminan duplicados comparando el texto sin espacios en sus extremos.
No se excluyen dificultades desconocidas, fuentes ni problemas sin tests:
estas restricciones no son necesarias para obtener los prompts. Pueden
quedar referencias a imágenes dentro del enunciado; no se descargan imágenes.
No se aplica el anterior umbral de 50 caracteres para evitar perder prompts
cortos válidos. El comando imprime cantidades leídas, exportadas y descartadas.

Opciones:

```bash
.venv/bin/python -m modeling.src.data.extract_prompts --split test
.venv/bin/python -m modeling.src.data.extract_prompts --min-chars 50
.venv/bin/python -m modeling.src.data.extract_prompts --keep-duplicates
.venv/bin/python -m modeling.src.data.extract_prompts --raw-dir /ruta/TACO --output /ruta/prompts.jsonl
```

El archivo de salida se reemplaza al completar la extracción; si falla la
lectura, se conserva la salida anterior. Los datos originales no se modifican.
Se procesa por lotes Arrow y solo la columna `question` se convierte a objetos
Python. No se necesita importar `datasets` (el entorno local revisado falla
al importarlo por ausencia de `_lzma`).

## Validación

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_extract_prompts.py' -v
```

## Notebooks ejecutables

Los tres notebooks resuelven la raíz del repositorio desde su propia carpeta.
Ya no necesitan `candidate_ids.csv`, `taco_candidates.parquet` ni `datasets`.

- `01_dataset_construction.ipynb`: exporta/reutiliza los prompts, carga una muestra,
  genera respuestas con Ollama opcionalmente y prepara tareas del sandbox.
- `data/prompts_por_nivel.ipynb`: exporta solo prompts a `processed/por_nivel/`.
  Deduplica dentro de cada dificultad; un mismo texto con etiquetas distintas
  puede aparecer en más de un archivo. Conserva dificultades desconocidas.
- `data/prompts_livecodebench.ipynb`: procesa `raw/livecodebench/test*.jsonl`
  cuando existen. Sin esos datos imprime `SIN DATOS` y termina sin exportar;
  ejecutar esa rama no valida la extracción real de LiveCodeBench.

Para volver a ejecutarlos y guardar sus salidas, usando el mismo Python:

```bash
.venv/bin/python -m pip install -r modeling/requirements-notebooks.txt
.venv/bin/python -m modeling.src.run_notebooks
```

## Adaptador de Ollama

`backend.local_llm.ollama_adapter.OllamaAdapter.generate(prompt)` es la única
operación de generación. Devuelve la respuesta completa de Ollama; el texto
se obtiene con `adapter.generate(prompt).response`. El calentamiento usa esa
misma operación con `options={"num_predict": 1}`. Las opciones por llamada no
modifican los valores predeterminados del adaptador.

`EvaluationRunner(adapter, hardware_monitor=None).evaluate(prompt)` añade
métricas alrededor del mismo adaptador, sin crear otro cliente ni copiar su
configuración. El monitor de hardware está en `hardware_monitor.py` y es
opcional: evaluar sin él no requiere NVIDIA/NVML. La generación del notebook y la CLI no
requieren el monitor de GPU. Host, timeout, keep_alive y cliente son configurables.

Migración: se eliminan `generate_result()`, `warm_up()` y `LLMGeneration`.
Usar `generate()`, `generate(..., options={"num_predict": 1})` y
`EvaluationRunner(adapter).evaluate()` respectivamente. Los consumidores que
esperaban texto de `generate()` deben acceder a `.response`. Todos los usos
presentes en este repositorio se actualizaron.

```bash
.venv/bin/python -m unittest discover -s tests -v
# Evaluación real: requiere Ollama y el modelo instalado; GPU/NVML opcionales.
.venv/bin/python -m modeling.src.evaluation.generate_responses \
  --input modeling/data/processed/prompts.jsonl \
  --run-dir modeling/experiments/runs/pilot-qwen3 \
  --model qwen3:8b --limit 3
```

La extracción de prompts funciona sin Ollama. El notebook puede generar
respuestas si RUN_OLLAMA=True. Las pruebas unitarias usan un cliente simulado.

## Flujo anterior conservado

`export_prompts.py` y los scripts de auditoría/candidatos se conservan por
compatibilidad. El `check_integrity.py` local apunta a `data/rawx/TACO`, aunque
los datos descargados están en `data/raw/TACO`; el nuevo flujo no lo utiliza.
No se modificaron esos cambios locales previos ni el manifiesto de descarga.

## Flujo de respuestas y preparación del sandbox

El notebook separa imports estándar, configuración de rutas e imports del
proyecto. La extracción solo se repite si falta el JSONL o se activa
`REBUILD_PROMPTS`. `load_prompts(path, limit=N)` carga progresivamente registros
`{prompt_id, prompt}`; el ID depende del texto y no del orden de las filas.

Configurar `MODEL`, `MAX_PROMPTS`, `OPTIONS`, `RUN_ID` y `RUN_OLLAMA=True`.
El valor predeterminado de RUN_OLLAMA es False para evitar inferencias al
volver a ejecutar automáticamente todos los notebooks. El piloto usa tres
prompts y qwen3:8b, modelo presente durante la validación local. La instrucción
de responder con Python se manda como system y se registra en la configuración.
No hay descarga automática de modelos.

Cada carpeta de ejecución contiene:

- `config.json`: modelo, endpoint, opciones, system y think.
- `responses.jsonl`: un intento por línea, prompt/response IDs, respuesta,
  estado, fecha, opciones y tiempos. Cada línea se vacía y sincroniza a disco.
- `sandbox_tasks.jsonl`: código candidato, límites y estado pendiente;
  no contiene resultados de ejecución.

`generate_batch` reanuda las respuestas completadas y reintenta los errores.
Rechaza reutilizar la carpeta si cambia la configuración. Una carpeta debe
tener un único escritor. Usar un nuevo RUN_ID para repetir un experimento o
cambiar la configuración; no se deducen garantías de reproducibilidad binaria
solo por fijar el nombre de un modelo local. Para publicaciones habrá que
registrar además el digest del modelo y versiones del runtime.

Las respuestas que agotan num_predict se marcan como incompletas al preparar
las tareas. La extracción de un bloque Python es deliberadamente conservadora;
respuestas sin bloque o con varios bloques requieren revisión. Los tests de
TACO se adjuntarán por separado mediante su procedencia split/idx y prompt_id.
La implementación y límites previstos se describen en
`modeling/src/sandbox/README.md`. Aún no hay ejecución de código generado.

### Validación local del piloto

Se generaron tres respuestas reales con qwen3:8b en
`modeling/experiments/runs/pilot_20261026_qwen3_notebook/`.
Las tres finalizaron con `done_reason=stop`; esto confirma que acabó la
generación, no que las soluciones sean correctas. Reanudar el mismo piloto
omite esas tres respuestas sin repetir inferencias. El notebook usa ese RUN_ID
para mostrar el resultado local y deja RUN_OLLAMA=False por defecto.

El primer enunciado es interactivo: su tarea requiere un juez dedicado.
Los otros dos siguen pendientes de adjuntar tests reales TACO. No se ejecutó
ninguna solución. Esta muestra valida el flujo de archivos e inferencia,
no es una selección representativa ni una evaluación de dificultad.
