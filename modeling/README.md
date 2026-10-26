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

## Revisión del flujo anterior

- `export_prompts.py` contiene `TacoDatasetBuilder`, que carga identificadores,
  pero no exporta prompts. Se conserva por compatibilidad.
- `01_dataset_construction.ipynb` anuncia LiveCodeBench, pero carga candidatos
  TACO; además intenta configurar imports después de importar el módulo.
- Los notebooks dentro de `modeling/notebooks/data/` usan `../data`, que desde
  esa carpeta apunta a `modeling/notebooks/data`, no a `modeling/data`.
- El notebook TACO depende de `taco_candidates.parquet`, ausente en esta copia.
  Los JSONL de LiveCodeBench tampoco están disponibles localmente.
- `check_integrity.py` apunta a `data/rawx/TACO`, mientras la descarga usa
  `data/raw/TACO`. El nuevo exportador usa la ruta de los datos existentes.
- Los scripts de candidatos aplican filtros por soluciones/tests ajenos al
  objetivo de extraer solo los enunciados.

Para la extracción usar el comando anterior. Se conservan los notebooks y
el código de auditoría existentes, incluidos los cambios locales previos.
LiveCodeBench no forma parte de esta salida porque no hay datos locales.
El backend y la generación de respuestas son flujos independientes.
