# Base del sandbox de evaluación

El notebook prepara tareas; ningún módulo de esta carpeta ejecuta respuestas.
`SandboxRunner` es un contrato sin implementación. Los límites son datos de
configuración propuestos, no restricciones ya aplicadas.

## Archivos y responsabilidades

- `contracts.py`: límites, resultado y protocolo del worker de ejecución.
- `prepare.py`: convierte respuestas generadas en `sandbox_tasks.jsonl`.
- Futuro `docker_runner.py`: implementación del worker fuera de Jupyter.
- Futuro `test_specs.py`: unión `prompt_id → split/idx TACO`, carga de
  `input_output`, modalidad stdin/función y comparación de resultados.

Una tarea incluye `task_id`, `prompt_id`, `response_id`, `language`, `code`,
`test_spec`, `limits` y `status`. `test_spec` comienza en null. No hay tareas
listas para ejecución hasta adjuntar tests reales y revisar la modalidad.
Un bloque Python extraído no implica que el código sea correcto ni seguro.
Las respuestas truncadas y ambiguas quedan marcadas y no deben ejecutarse.
Los enunciados que declaran "interactive problem" se marcan como
`requires_interactive_judge`: necesitan un juez interactivo. Esta detección
textual es orientativa; la modalidad se debe confirmar en los metadatos/tests.

El futuro test_spec debe tener origen (dataset/revisión/split/idx), modalidad,
inputs/outputs y, para funciones, nombre/contrato de llamada. Los tests deben
mantenerse separados del texto enviado al modelo. Un mismo prompt puede
corresponder a varias filas TACO: la unión debe detectar esa ambigüedad.

## Dónde ejecutarlo

Desarrollar el worker en `modeling/src/sandbox/` y ejecutar cada solución en
un contenedor Linux efímero dentro de una VM dedicada. Para el piloto local,
se puede usar una VM de Docker Desktop; para lotes, una VM Linux dedicada al
worker. Ollama permanece fuera del contenedor que ejecuta la solución.

El worker deberá fijar imagen por digest, usuario sin privilegios, red
inactiva, raíz de solo lectura, filesystem temporal acotado, capacidades
eliminadas y no-new-privileges. Debe aplicar CPU, memoria y procesos, matar el
contenedor al vencer el tiempo, limitar stdout/stderr y limpiar en finally.
No montar el repositorio completo, credenciales ni el socket Docker dentro
del contenedor. El límite de CPU no sustituye al límite de tiempo de pared.
El contenedor no es una garantía absoluta: para código no confiable se
mantiene además la frontera de una VM aislada, sin secretos.

Referencias oficiales:
- https://docs.docker.com/engine/security/
- https://docs.docker.com/engine/containers/resource_constraints/

Los resultados futuros se guardarán en `sandbox_results.jsonl`, enlazados por
`task_id`, con estado, salida, error, código de retorno y duración. Solo después
se calculan métricas de corrección o dificultad; las tareas pendientes no
cuentan como fallos de la solución.
