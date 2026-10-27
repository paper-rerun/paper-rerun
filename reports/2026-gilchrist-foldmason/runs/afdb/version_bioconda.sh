#!/bin/bash
# Version check of the bioconda build of FoldMason 4-dd3c235
FM=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/env/bioconda/mamba/envs/foldmason/bin/foldmason
nice -n 19 "$FM" version
