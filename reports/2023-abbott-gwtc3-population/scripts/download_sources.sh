#!/bin/bash
# Download only what the PP run and the pre-registration need, verify size and md5
set -u
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/sources
get() { # url name size md5
  url="$1"; name="$2"; size="$3"; md5="$4"
  if [ ! -f "$name" ] || [ "$(stat -c %s "$name")" != "$size" ]; then
    curl -sSL --retry 5 -C - -o "$name" "$url" || curl -sSL --retry 5 -o "$name" "$url"
  fi
  got_size=$(stat -c %s "$name"); got_md5=$(md5sum "$name" | cut -d' ' -f1)
  echo "$name size=$got_size expected=$size md5=$got_md5 expected=$md5 $([ "$got_size" = "$size" ] && [ "$got_md5" = "$md5" ] && echo OK || echo FAIL)"
}
Z=https://zenodo.org/records/11254021/files
get "$Z/table_data.tar.gz" table_data.tar.gz 4888 4fed132ca7fcdbb7bfb9b1a1448b4df0
get "$Z/README.md" README_zenodo.md 11143 b41d172c27e32ac81c5e50c5dd05e42a
get "$Z/GWTC-3-population_py_requirements.txt" GWTC-3-population_py_requirements.txt 267 0e307a6ef64788a2999ea9e780257398
get "$Z/GWTC-3-population-data.tar.gz" GWTC-3-population-data.tar.gz 40257247 01197cae2dd3abf7280307fd35a883a9
get "https://zenodo.org/records/5636816/files/o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5" "o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5" 63149928 c21337a25b7318fdfd471cce549a547e
get "$Z/analyses_PowerLawPeak.tar.gz" analyses_PowerLawPeak.tar.gz 793638616 85c3b6599287e8083005e2a18778cb36
