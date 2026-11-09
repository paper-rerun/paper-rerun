#!/bin/bash
set -e
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export UV_CACHE_DIR=$W/env/uv-cache
cd $W/env
uv venv -p 3.10 venv
uv pip install -p venv/bin/python la_forge numpy scipy h5py emcee matplotlib
uv pip freeze -p venv/bin/python > requirements.lock
cat requirements.lock
