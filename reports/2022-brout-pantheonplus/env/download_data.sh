#!/bin/bash
# Fetch distances and covariance at the pinned commit; check size, md5 and git blob sha1
set -euo pipefail
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus/data
C=c447f0fea703fcd0fff57de5000947b5ca81286b
BASE="https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/$C/Pantheon%2B_Data/4_DISTANCES_AND_COVAR"
while read -r name url size md5 blob; do
  if [ ! -f "$name" ] || [ "$(stat -c %s "$name")" != "$size" ]; then
    curl -sSfL --retry 3 -o "$name.part" "$BASE/$url"
    mv "$name.part" "$name"
  fi
  srv=$(curl -sSfLI "$BASE/$url" | grep -i '^content-length' | tail -1 | tr -d '\r' | awk '{print $2}')
  got=$(stat -c %s "$name")
  gmd5=$(md5sum "$name" | cut -d' ' -f1)
  gblob=$( (printf 'blob %s\0' "$got"; cat "$name") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$size" ] && [ "$gmd5" = "$md5" ] && [ "$gblob" = "$blob" ] && ok=OK || ok=FAIL
  echo "$ok $name size=$got expected=$size server_content_length=$srv md5=$gmd5 gitblob=$gblob sha256=$(sha256sum "$name" | cut -d' ' -f1)"
done <<'LIST'
Pantheon+SH0ES.dat Pantheon%2BSH0ES.dat 579283 2049b142e6aad384470b3364aa10f3fa cce857db0c15e9ce7a0e0ce77452b6ff62af969a
Pantheon+SH0ES_STAT+SYS.cov Pantheon%2BSH0ES_STAT%2BSYS.cov 33284960 041bdb6638841794fc2d7caa88dd66eb d1a1498154e7ba826df14bdbef35ebcb7f5efba1
LIST
