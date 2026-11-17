#!/bin/bash
cd /mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego
git clone https://github.com/ACEsuit/mace-off.git repo 2>&1 | tail -2
cd repo && git log -3 --format='%H %ci %s' && git lfs ls-files 2>&1 | head; ls -laR | head -60
cd ..
curl -sSL -w "\n%{http_code}\n" https://doi.org/10.17863/CAM.107498 -o data/apollo_landing.html; echo rc=$?
curl -sSL "https://api.github.com/repos/ACEsuit/mace-off/issues?state=all&per_page=100" -o logs/mace_off_issues.json; echo rc=$?
