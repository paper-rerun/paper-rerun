#!/bin/bash
# Rebuild the environment from scratch. With --compile it also re-resolves the lockfile (only needed if requirements.in changes)
set -eu
E=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/env
R=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo
UV=~/.local/bin/uv
# Cache lives on ext4 and the venv on /mnt/e, so hardlinks are not possible
export UV_LINK_MODE=copy

if [ "${1:-}" = "--compile" ]; then
	# Authors' full env list goes in as constraints so every transitive dependency keeps their pin
	grep -v '^#' "$R/environments/proteingym_env.txt" > "$E/authors_constraints.txt"
	$UV pip compile --python-version 3.10 --python-platform x86_64-manylinux_2_28 --generate-hashes \
		-c "$E/authors_constraints.txt" "$E/requirements.in" -o "$E/requirements.lock"
fi

rm -rf "$E/venv"
$UV venv --python 3.10.14 "$E/venv"
$UV pip sync --python "$E/venv/bin/python" --require-hashes "$E/requirements.lock"
$UV pip freeze --python "$E/venv/bin/python" > "$E/freeze.txt"
"$E/venv/bin/python" -c "import torch, numpy, pandas, scipy, sklearn, Bio, numba; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'gpu', torch.cuda.is_available())"
