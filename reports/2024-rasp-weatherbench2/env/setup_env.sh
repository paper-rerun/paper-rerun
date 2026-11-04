#!/bin/bash
# Rebuild the env from the frozen lockfile. Resolution was done with --exclude-newer 2024-01-26 (arXiv v2 / commit 156e5dc date)
set -e
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/env
export UV_LINK_MODE=copy
UV=~/.local/bin/uv
if [ ! -f requirements.lock ]; then
	$UV pip compile requirements.in --python-version 3.11 --exclude-newer 2024-01-26 -o requirements.lock
fi
[ -d .venv ] || $UV venv --python 3.11 .venv
$UV pip install --python .venv/bin/python -r requirements.lock
$UV pip install --python .venv/bin/python --no-deps -e ../repo/weatherbench2
.venv/bin/python -c "import weatherbench2, xarray, zarr, numcodecs, pandas, apache_beam; print('ok', xarray.__version__, zarr.__version__, pandas.__version__, apache_beam.__version__)"
