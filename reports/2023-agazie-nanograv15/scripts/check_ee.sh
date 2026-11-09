#!/bin/bash
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export UV_CACHE_DIR=$W/env/uv-cache
uv pip install -q --no-deps --target $W/env/ee_src enterprise_extensions 2>&1 | tail -2
ls $W/env/ee_src | grep -i enterprise
grep -n "def model_general" -A 12 $W/env/ee_src/enterprise_extensions/models.py | grep -n -E "gamma_common|def model_general"
grep -n "gamma_common" $W/env/ee_src/enterprise_extensions/blocks.py | head -8
cd $W; sha256sum claims.json; cat claims.sha256
ls / | tr '\n' ' '
