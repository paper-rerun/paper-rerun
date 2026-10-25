# Rebuilds the whole environment from scratch: repo at v1.3.0, venv in env/.venv, packages from the frozen lock.
# Usage (WSL): bash /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/setup.sh
set -e
ROOT=/mnt/e/Ciencia/pipeline/2025-ko-matgl
UV=$HOME/.local/bin/uv
# venv lives on /mnt/e, cache on ext4, so no hardlinks
export UV_LINK_MODE=copy
cd $ROOT
[ -d repo/.git ] || git clone https://github.com/materialyzeai/matgl.git repo
git -C repo checkout -q a6ebaebd6a0021e14d49d001103508c4980d94da
rm -rf env/.venv
$UV venv --python 3.12.15 env/.venv
$UV pip sync --python env/.venv/bin/python --index-strategy unsafe-best-match env/requirements.lock.txt
# matgl itself, editable, without touching the locked deps
$UV pip install --python env/.venv/bin/python --no-deps --no-sources -e repo
$UV pip freeze --python env/.venv/bin/python > env/pip_freeze.txt
echo setup done
