# Blind-verify env: fresh clone of matgl at v1.3.0 and a new venv from the frozen lock, all under verify/
set -e
ROOT=/mnt/e/Ciencia/pipeline/2025-ko-matgl
V=$ROOT/verify
UV=$HOME/.local/bin/uv
export UV_LINK_MODE=copy
cd $V
[ -d repo/.git ] || git clone -q https://github.com/materialyzeai/matgl.git repo
git -C repo checkout -q a6ebaebd6a0021e14d49d001103508c4980d94da
git -C repo rev-parse HEAD
git -C repo status --porcelain | head
rm -rf env
$UV venv --python 3.12.15 env
$UV pip sync --python env/bin/python --index-strategy unsafe-best-match $ROOT/env/requirements.lock.txt
$UV pip install --python env/bin/python --no-deps --no-sources -e repo
$UV pip freeze --python env/bin/python > pip_freeze_verify.txt
diff <(grep -v '^-e' $ROOT/env/pip_freeze.txt) <(grep -v '^-e' pip_freeze_verify.txt) && echo "freeze matches env/pip_freeze.txt (except editable line)"
echo setup done
