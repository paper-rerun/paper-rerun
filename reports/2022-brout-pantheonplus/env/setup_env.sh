#!/bin/bash
# Build the venv with 2022-era versions from PyPI (the authors ran CosmoSIS in 07/2022; no version pins were released)
# REBUILD_FROM_LOCK=1 reinstalls exactly env/requirements.lock.txt
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus
export PATH=$HOME/.local/bin:$PATH
export UV_LINK_MODE=copy
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
uv venv --clear --python 3.10 env/.venv
source env/.venv/bin/activate
if [ "${REBUILD_FROM_LOCK:-0}" = 1 ]; then
  nice -n 19 uv pip install --build-constraint env/build_constraints.txt -r env/requirements.lock.txt
else
  # camb 1.3.5 is an sdist (Fortran, built with gfortran); its setup.py imports pkg_resources, so the build uses setuptools<70
  # Releases current in mid-2022: numpy 1.22, scipy 1.8, pandas 1.4, emcee 3.1.2, dynesty 1.2.3, camb 1.3.5
  nice -n 19 uv pip install --build-constraint env/build_constraints.txt "numpy==1.22.4" "scipy==1.8.1" "pandas==1.4.3" "emcee==3.1.2" "dynesty==1.2.3" "camb==1.3.5" "matplotlib==3.5.2"
  uv pip freeze > env/requirements.lock.txt
fi
python -c "import numpy, scipy, pandas, emcee, dynesty, camb; print(numpy.__version__, scipy.__version__, pandas.__version__, emcee.__version__, dynesty.__version__, camb.__version__)"
