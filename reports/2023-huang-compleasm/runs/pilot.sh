R=/mnt/e/Ciencia/noturno/2023-huang-compleasm
bash $R/data/prep_library.sh odb10
bash $R/runs/run_one.sh scer GCF_000146045.2_R64 saccharomycetes_odb10
tail -12 $R/runs/scer/run.log; grep -E "Elapsed|Maximum resident" $R/runs/scer/time.txt
