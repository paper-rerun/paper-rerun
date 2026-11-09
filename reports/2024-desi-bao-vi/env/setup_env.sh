#!/usr/bin/env bash
# Build the frozen environment for the DESI 2024 VI rerun.
# Resolved as of the arXiv v3 date of the paper, so we start from versions the
# authors could plausibly have used instead of whatever is newest today.
set -euo pipefail

ROOT=/mnt/e/Ciencia/noturno/2024-desi-bao-vi
cd "$ROOT/env"

export UV_CACHE_DIR="$ROOT/env/.uv-cache"
EXCLUDE_NEWER=2024-04-05   # arXiv submission date of 2404.03002

cat > requirements.in <<'EOF'
numpy
scipy
camb
cobaya
getdist
EOF

nice -n 19 uv pip compile requirements.in \
  --exclude-newer "$EXCLUDE_NEWER" \
  --python-version 3.11 \
  -o requirements.lock

nice -n 19 uv venv --python 3.11 "$ROOT/env/venv"
VIRTUAL_ENV="$ROOT/env/venv" nice -n 19 uv pip install -r requirements.lock

"$ROOT/env/venv/bin/python" -c "import numpy,scipy,camb,cobaya,getdist; \
print('numpy',numpy.__version__); print('scipy',scipy.__version__); \
print('camb',camb.__version__); print('cobaya',cobaya.__version__); \
print('getdist',getdist.__version__)"
