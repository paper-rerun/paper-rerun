#!/bin/bash
# Rebuild the environment of the PP rerun from scratch (WSL2 Ubuntu 24.04, uv). Then: source env/activate.sh
set -e
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env
export PATH=$HOME/.local/bin:$PATH
# 1. Python 3.8 (3.7.3 in the original run; uv cannot fetch 3.7) and the pinned stack
uv python install 3.8
[ -d venv ] || uv venv -p 3.8 venv
uv pip install -p venv/bin/python -r requirements.in
# bilby_pipe is imported only for convert_string_to_dict; its import chain needs these
uv pip install -p venv/bin/python --no-deps bilby_pipe==1.0.4
uv pip install -p venv/bin/python configargparse==1.5.3 pycondor==0.5.0 gwosc==0.5.6 requests jinja2==2.10.1 markupsafe==1.1.1
# 2. gwpopulation_pipe at the commit recorded in the published result
[ -d gwpopulation_pipe_src ] || git clone -q https://git.ligo.org/RatesAndPopulations/gwpopulation_pipe.git gwpopulation_pipe_src
git config --global --add safe.directory "$PWD/gwpopulation_pipe_src"
(cd gwpopulation_pipe_src && git fetch -q origin 83c9bb97a755690a2d42930ff4ae43f239254cc2 && git checkout -q 83c9bb97a755690a2d42930ff4ae43f239254cc2)
uv pip install -p venv/bin/python --no-deps ./gwpopulation_pipe_src
# 3. CUDA 11.1 runtime libraries for cupy-cuda111 8.4.0, unpacked locally (checks size + sha256 against NVIDIA's apt index)
bash cuda_get.sh
