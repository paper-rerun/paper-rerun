set -e
cd /mnt/e/Ciencia/pipeline/2025-ko-matgl/repo
~/.local/bin/uv export --frozen --no-hashes --no-emit-project --no-dev --python 3.12 2>&1 | grep -v '^ *#' > /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/authors_uvlock_export.txt
wc -l /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/authors_uvlock_export.txt
grep -n -A12 '^\[project.optional-dependencies\]\|^\[dependency-groups\]' pyproject.toml | head -40
