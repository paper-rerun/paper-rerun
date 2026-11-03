#!/bin/bash
# Human retry after the OOM kill (attempt 1 died at 20.4 GB anon RSS while another job shared WSL memory)
R=/mnt/e/Ciencia/noturno/2023-huang-compleasm/runs
until grep -q ALL_RUNS_FINISHED $R/run_all.log; do sleep 30; done
[ -d $R/hsap ] && [ ! -s $R/hsap/summary.txt ] && mv $R/hsap $R/hsap_attempt1_oom
free -m | head -2
bash $R/run_one.sh hsap GCF_009914755.1_T2T-CHM13v2.0 primates_odb10
echo HSAP_RETRY_FINISHED rc=$?
