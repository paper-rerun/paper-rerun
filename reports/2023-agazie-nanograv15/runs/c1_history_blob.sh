#!/bin/bash
# No git fetch possible: only GIT_NO_LAZY_FETCH=1 reads, and packs are listed before and after
W=/mnt/e/Ciencia/noturno/2023-agazie-nanograv15
export MPLBACKEND=Agg OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6 GIT_NO_LAZY_FETCH=1
R=$W/sources/repo
echo '--- packs before'; ls -l $R/.git/objects/pack/ | awk '{print $5, $9}'
echo '--- figure1_data tree in parent of 98a4783 (no lazy fetch)'
git -C $R log -1 --format='%H %ci %s' 98a4783
git -C $R ls-tree -r 98a4783^ -- data_release/figure_1/figure1_data/
echo '--- commit that added it'; git -C $R log --diff-filter=A --format='%H %ci %s' -- data_release/figure_1/figure1_data/nano15_hd_chain_fg_long_050523.npy
echo '--- enterprise_extensions gamma_common default and Constant'
grep -n "gamma_common" $W/env/ee_src/enterprise_extensions/models.py | sed -n 1,40p | grep -E "^(811|1080):"
grep -n -E "gamma_val is not None|parameter.Constant\(gamma_val\)|Uniform\(-18, -11\)" $W/env/ee_src/enterprise_extensions/blocks.py | head
cd $W/runs; nice -n 19 $W/env/venv/bin/python -I c1_history_blob.py $W
echo '--- packs after'; ls -l $R/.git/objects/pack/ | awk '{print $5, $9}'
echo '--- sizes'; du -sh $W $W/sources $W/env $W/review_scratch
