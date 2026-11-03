#!/bin/bash
# Primary runs in the pre-registered order, one at a time (human runs alone)
R=/mnt/e/Ciencia/noturno/2023-huang-compleasm/runs
bash $R/run_one.sh scer GCF_000146045.2_R64 saccharomycetes_odb10
bash $R/run_one.sh cele GCF_000002985.6_WBcel235 nematoda_odb10
bash $R/run_one.sh atha GCF_000001735.4_TAIR10.1 brassicales_odb10
bash $R/run_one.sh dmel GCF_000001215.4_Release_6_plus_ISO1_MT diptera_odb10
bash $R/run_one.sh mmus GCF_000001635.27_GRCm39 glires_odb10
bash $R/run_one.sh hsap GCF_009914755.1_T2T-CHM13v2.0 primates_odb10
bash $R/run_one.sh zmay GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0 liliopsida_odb10
# Not graded: determinism repeat and the --outs 0.97 variant on the 4 small genomes
bash $R/run_one.sh scer_rep GCF_000146045.2_R64 saccharomycetes_odb10
bash $R/run_one.sh outs097_scer GCF_000146045.2_R64 saccharomycetes_odb10 0.97
bash $R/run_one.sh outs097_cele GCF_000002985.6_WBcel235 nematoda_odb10 0.97
bash $R/run_one.sh outs097_atha GCF_000001735.4_TAIR10.1 brassicales_odb10 0.97
bash $R/run_one.sh outs097_dmel GCF_000001215.4_Release_6_plus_ISO1_MT diptera_odb10 0.97
echo ALL_RUNS_FINISHED
