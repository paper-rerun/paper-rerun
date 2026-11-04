#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env
export PATH=$HOME/.local/bin:$PATH
uv pip install -q -p venv/bin/python setuptools==59.8.0
venv/bin/python -c "import tables, deepdish; print('tables', tables.__version__, 'deepdish ok')"
uv pip freeze -p venv/bin/python > requirements.lock
