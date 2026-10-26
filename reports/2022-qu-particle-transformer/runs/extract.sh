#!/bin/bash
# Extract the test tar into data/JetClass (list first, then extract, then list file sizes)
set -eu
D=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer/data
cd $D
tar -tvf JetClass_Pythia_test_20M.tar > tar_listing.txt
mkdir -p JetClass
tar -xf JetClass_Pythia_test_20M.tar -C JetClass --no-same-owner
find JetClass -type f -name '*.root' | wc -l
echo extract done
