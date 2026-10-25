#!/bin/bash
# Fetch COMP6 v1 (pinned commit) and the HF copies of the weights; check size and git blob sha1 / sha256.
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2025-ko-matgl
C=79f41c156f8e19506fe951b5513b98e7c534a503
mkdir -p data/COMP6 data/hf
while read -r path size blob; do
  out=data/COMP6/$path
  mkdir -p "$(dirname "$out")"
  if [ ! -f "$out" ] || [ "$(stat -c %s "$out")" != "$size" ]; then
    curl -sSfL --retry 3 -o "$out.part" "https://raw.githubusercontent.com/isayev/COMP6/$C/$path"
    mv "$out.part" "$out"
  fi
  got=$(stat -c %s "$out")
  gblob=$( (printf 'blob %s\0' "$got"; cat "$out") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$size" ] && [ "$gblob" = "$blob" ] && ok=OK || ok=FAIL
  echo "$ok $path size=$got/$size gitblob=$gblob sha256=$(sha256sum "$out" | cut -d' ' -f1)"
done < env/comp6_expected.txt
for m in M3GNet SO3Net TensorNet; do
  repo=materialyze/$m-PES-ANI-1x-Subset
  mkdir -p data/hf/$m
  for f in state.pt model.json; do
    [ -f data/hf/$m/$f ] || curl -sSfL --retry 3 -o data/hf/$m/$f "https://huggingface.co/$repo/resolve/main/$f" || echo "MISSING $repo/$f"
  done
  echo "HF $m: $(sha256sum data/hf/$m/state.pt | cut -c1-64) tag: $(sha256sum data/matgl/pretrained_models/$m-ANI-1x-Subset-PES/state.pt | cut -c1-64)"
done
