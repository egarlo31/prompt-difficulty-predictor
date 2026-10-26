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

- `01_dataset_construction.ipynb`: exporta y valida los 25,816 prompts únicos.
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

`backend.local_llm.ollama_adapter.OllamaAdapter` concentra las llamadas a
Ollama del backend y del evaluador. `generate(prompt)` conserva la respuesta
como texto; `generate_result(prompt)` devuelve la respuesta completa con
métricas. `warm_up()` usa la misma ruta con un token de salida. Las opciones
por llamada se combinan con los valores predeterminados sin modificarlos.
Host, timeout, keep_alive y cliente son configurables. Las pruebas inyectan
un cliente simulado y no requieren un servidor ni descargan modelos.

```bash
.venv/bin/python -m unittest discover -s tests -v
# Evaluación real: requiere Ollama, el modelo instalado y GPU NVIDIA/NVML.
.venv/bin/python -m modeling.src.evaluation.generate_responses
```

La ejecución real de Ollama es independiente de extraer prompts y de los
notebooks. Las pruebas del adaptador no demuestran conectividad al servidor.

## Flujo anterior conservado

`export_prompts.py` y los scripts de auditoría/candidatos se conservan por
compatibilidad. El `check_integrity.py` local apunta a `data/rawx/TACO`, aunque
los datos descargados están en `data/raw/TACO`; el nuevo flujo no lo utiliza.
No se modificaron esos cambios locales previos ni el manifiesto de descarga.
