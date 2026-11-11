#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_LINK_MODE=copy
uv venv --clear --python 3.12 venv
VP=./venv/bin/python
uv pip install --python "$VP" "openpyxl==3.1.5" "numpy==2.1.3" "pandas==2.2.3"
uv pip freeze --python "$VP" > env-freeze-stage1.txt
$VP -V
