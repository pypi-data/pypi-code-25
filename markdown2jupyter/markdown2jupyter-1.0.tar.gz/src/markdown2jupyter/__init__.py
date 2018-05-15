from enum import Enum
from nbconvert.preprocessors import ExecutePreprocessor
import json
import nbformat


class CellType(Enum):

    MARKDOWN = 1
    PYTHON = 2
    RAW = 3


def create_executor(path, timeout):
    ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    return (lambda ntb: ep.preprocess(ntb, {'metadata': {'path': path}})[0])


def markdown2jupyter(markdown_file, jupyter_file, preprocessor=None, version=None):
    if version is None:
        version = nbformat.v4
    notebook = version.new_notebook(cells=[
        chunk2cell(chunk, version) for chunk in load_markdown_chunks(markdown_file)
    ])
    if preprocessor:
        notebook = preprocessor(notebook)
    with open(jupyter_file, 'w') as f:
        json.dump(notebook, f)


def chunk2cell(chunk, version=None):
    if version is None:
        version = nbformat.v4
    cell_type, cell_content = chunk
    if cell_type == CellType.MARKDOWN:
        return version.new_markdown_cell(cell_content)
    if cell_type == CellType.PYTHON:
        return version.new_code_cell(cell_content)
    return version.new_raw_cell(cell_content)


def load_markdown_chunks(filename):
    so_far = []
    cell_type = None
    with open(filename, 'r') as f:
        for line in f:
            if not line.startswith('```'):
                so_far.append(line)
                cell_type = cell_type if cell_type is not None else CellType.MARKDOWN
                continue
            if cell_type:
                yield cell_type, ''.join(so_far).strip()
            if cell_type == CellType.MARKDOWN:
                cell_type = CellType.PYTHON if line.startswith('```python') else CellType.RAW
            else:
                cell_type = None
            so_far = []
    rest = ''.join(so_far)
    if rest and cell_type:
        yield cell_type, so_far
