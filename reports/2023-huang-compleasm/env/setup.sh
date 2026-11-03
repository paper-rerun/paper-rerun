#!/bin/bash
# Builds the compleasm v0.2.2 environment: release kit (md5-checked) + uv venv with Python 3.10, pandas 2.0.2
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-huang-compleasm
ENV=$ROOT/env
DL=$ROOT/dl/kit
mkdir -p "$DL" "$ENV/bin"
URL=https://github.com/huangnengCSU/compleasm/releases/download/v0.2.2/compleasm-0.2.2_x64-linux.tar.bz2
TAR=$DL/compleasm-0.2.2_x64-linux.tar.bz2
if [ ! -s "$TAR" ]; then curl -fsSL -o "$TAR" "$URL"; fi
REMOTE=$(curl -fsSLI "$URL" | grep -i '^content-length' | tail -1 | tr -dc 0-9)
LOCAL=$(stat -c %s "$TAR")
echo "kit size local=$LOCAL server=$REMOTE"
[ "$LOCAL" = "$REMOTE" ]
echo "cefe5b8d17c3758add056af1cf4e40a5  $TAR" | md5sum -c -
echo "9c28fd0ebf0986475c4e567038b8bffc93ef795e76982401e84531885227e8a5  $TAR" | sha256sum -c -
tar -xjf "$TAR" -C "$DL"
# Copy out of dl/ before running anything
KIT=$(dirname "$(find "$DL" -name compleasm.py | head -1)")
cp "$KIT/compleasm.py" "$KIT/miniprot" "$KIT/hmmsearch" "$ENV/bin/"
chmod +x "$ENV/bin/miniprot" "$ENV/bin/hmmsearch"
md5sum "$ENV/bin/"* | tee "$ENV/kit_md5.txt"
cd "$ENV"
export UV_PROJECT_ENVIRONMENT="$ENV/.venv"
~/.local/bin/uv venv --python 3.10 "$ENV/.venv"
~/.local/bin/uv pip install --python "$ENV/.venv/bin/python" pandas==2.0.2 "numpy==1.24.3"
~/.local/bin/uv pip freeze --python "$ENV/.venv/bin/python" | tee "$ENV/requirements.lock"
"$ENV/.venv/bin/python" --version
"$ENV/bin/miniprot" --version
"$ENV/bin/hmmsearch" -h | sed -n 2p
grep -n '__version__' "$ENV/bin/compleasm.py" | head -2
