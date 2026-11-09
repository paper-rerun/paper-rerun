#!/usr/bin/env bash
# Diagnostic only, not the route of this rerun: fetch the authors' own
# published chain for flat LCDM, DESI BAO + BBN, so we can compare their
# r_drag and H0 marginals with ours. TLS verification stays on throughout.
set -euo pipefail
B="https://data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0"
DEST=/mnt/e/Ciencia/noturno/2024-desi-bao-vi/data/official
mkdir -p "$DEST"
cd "$DEST"

listing() {
  nice -n 19 curl -sS -m 90 "$1" | grep -oE 'href="[^"]+"' | sed 's/href="//; s/"$//'
}

if [ "${1:-walk}" = "walk" ]; then
  for p in "" "/cobaya" "/cobaya/base" "/cobaya/base/desi-bbn" \
           "/cobaya/base/desi_bbn"; do
    echo "### ${B}${p}/"
    listing "${B}${p}/" | head -40 || true
  done
  exit 0
fi

# Second mode: download every file under the directory given as $1.
SUB="$1"
mkdir -p "$DEST/$(basename "$SUB")"
cd "$DEST/$(basename "$SUB")"
for f in $(listing "${B}/${SUB}/"); do
  case "$f" in
    ../|*/) continue ;;
  esac
  echo "get $f"
  nice -n 19 curl -sSf -m 300 -O "${B}/${SUB}/${f}"
done
ls -la
