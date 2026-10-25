#!/bin/bash
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-ko-matgl/data
if [ ! -d matgl ]; then
  git clone --quiet --branch v1.3.0 --depth 1 https://github.com/materialyzeai/matgl.git matgl
fi
cd matgl
git rev-parse HEAD
git log -1 --format=%cd
sed -n '1,80p' pyproject.toml
ls pretrained_models | grep ANI
ls -la pretrained_models/*ANI-1x-Subset*/
sha256sum pretrained_models/*ANI-1x-Subset*/*
