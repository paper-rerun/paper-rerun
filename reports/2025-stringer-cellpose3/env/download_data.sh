#!/bin/bash
# Public data used for the reproduction. CARE (CC0, Edmond doi:10.17617/3.FDFZOF), ribo two-photon (CC BY-NC 4.0, figshare 27854442)
set -e
D=/mnt/e/Ciencia/artigos/2025-stringer-cellpose3/data
mkdir -p $D/care $D/ribo
cd $D/care
# Only the test_data folders are kept
curl -sL https://edmond.mpg.de/api/access/datafile/264096 | tar xz --wildcards '*test_data*' && echo flywing ok
curl -sL https://edmond.mpg.de/api/access/datafile/264091 | tar xz --wildcards '*test_data*' && echo tribolium ok
cd $D/ribo
for p in "1 50632449" "3 50632437" "4 50632428" "5 50632431" "6 50632434"; do
  set -- $p
  curl -sL -o denoise_0000$1_00001.tif https://ndownloader.figshare.com/files/$2 && echo ribo $1 ok
done
ls -laR $D | head -80
