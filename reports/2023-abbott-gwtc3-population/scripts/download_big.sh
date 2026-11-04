#!/bin/bash
# Parallel download of the two big files with aria2c, then size + md5 check
set -u
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/sources
pkill -f download_sources.sh; pkill -f "curl -sSL --retry 5"
check() { name="$1"; size="$2"; md5="$3"
  got_size=$(stat -c %s "$name"); got_md5=$(md5sum "$name" | cut -d' ' -f1)
  echo "$name size=$got_size expected=$size md5=$got_md5 expected=$md5 $([ "$got_size" = "$size" ] && [ "$got_md5" = "$md5" ] && echo OK || echo FAIL)"; }
rm -f "o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5"
aria2c -q -x8 -s8 --file-allocation=none -o "o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5" "https://zenodo.org/records/5636816/files/o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5"
check "o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5" 63149928 c21337a25b7318fdfd471cce549a547e
aria2c -q -x8 -s8 --file-allocation=none -o analyses_PowerLawPeak.tar.gz "https://zenodo.org/records/11254021/files/analyses_PowerLawPeak.tar.gz"
check analyses_PowerLawPeak.tar.gz 793638616 85c3b6599287e8083005e2a18778cb36
echo ALLDONE
