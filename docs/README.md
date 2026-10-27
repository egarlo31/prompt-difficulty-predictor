# Project documentation

This documentation describes the checked-out implementation as reviewed on
2026-10-26. Proposed model training and code execution are explicitly marked as
pending. Repository code and stored artifacts are the evidence for current status.

- [Definition and current state](project/01_project_definition.md)
- [Implemented scope and limits](project/02_project_scope.md)
- [Practical next steps](project/03_project_plan.md)
- [Task status](project/04_tasks.md)
- [Current architecture](architecture/01_architecture_overview.md)
- [Dataset sources](data/data_research.md)
- [Local TACO audit](data/01_data_audit.md)
- [Prompt ID traceability verification](data/02_prompt_traceability.md)

The current system prepares prompts, generates experimental responses through
Ollama, and exposes a provisional difficulty API with a browser interface.
It does not yet train a difficulty model or execute generated solutions in a sandbox.

Older SVG/draw.io sketches under `architecture/` describe prospective designs.
They are retained as historical references; the architecture document above is
the description of the current implementation.

`modeling/README.md` is outside this documentation update and still contains
references to removed modules. Use the code paths and notebook names documented
here; the obsolete commands in that README were not edited.
