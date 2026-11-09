#!/bin/bash
# Build the pinned env inside the work folder, CPU only
set -e
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego
export UV_CACHE_DIR=$W/env/uv-cache
export UV_PYTHON_INSTALL_DIR=$W/env/uv-python-cache
cd $W/env
uv --version
nice -n 19 uv venv --python 3.10 venv
cat > requirements.in <<'R'
la_forge==1.1.0
numpy==1.24.4
scipy==1.10.1
h5py==3.9.0
emcee==3.1.4
matplotlib==3.7.2
pandas==2.0.3
R
nice -n 19 uv pip compile requirements.in -o requirements.lock --python venv/bin/python
nice -n 19 uv pip install --python venv/bin/python -r requirements.lock
venv/bin/python -c "import la_forge, numpy, scipy, h5py, emcee; print('la_forge', la_forge.__version__ if hasattr(la_forge,'__version__') else '?', 'numpy', numpy.__version__, 'scipy', scipy.__version__, 'h5py', h5py.__version__, 'emcee', emcee.__version__)"
