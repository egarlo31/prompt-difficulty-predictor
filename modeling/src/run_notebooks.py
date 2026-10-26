"""Execute project notebooks using the invoking Python environment."""
from pathlib import Path
import os
import sys
import json
import tempfile
with tempfile.TemporaryDirectory() as directory:
    kernels = Path(directory) / 'kernels' / 'project-python'
    kernels.mkdir(parents=True)
    (kernels / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Project Python', 'language': 'python',
    }))
    os.environ['JUPYTER_PATH'] = directory
    import nbformat
    from nbclient import NotebookClient
    for path in sorted((Path(__file__).resolve().parents[1] / 'notebooks').rglob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=180, kernel_name='project-python',
                       resources={'metadata': {'path': str(path.parent.resolve())}}).execute()
        nbformat.write(notebook, path)
        print('EXECUTED:', path, flush=True)
        for cell in notebook.cells:
            for output in cell.get('outputs', []):
                if output.output_type == 'stream':
                    print(output.text, end='', flush=True)
