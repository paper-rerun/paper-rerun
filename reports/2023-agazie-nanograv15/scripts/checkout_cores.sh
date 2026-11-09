#!/bin/bash
set -e
cd /mnt/e/Ciencia/noturno/2023-agazie-nanograv15/sources/repo
git sparse-checkout disable
git status --short | head
ls -l tutorials/presampled_cores/
sha256sum tutorials/presampled_cores/*.core data_release/figure_3/pshift_bfs.npy
