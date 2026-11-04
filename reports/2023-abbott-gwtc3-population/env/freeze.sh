#!/bin/bash
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env
~/.local/bin/uv pip freeze -p venv/bin/python > requirements.lock
venv/bin/python -V >> requirements.lock.python
