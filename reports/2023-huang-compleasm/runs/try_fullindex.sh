R=/mnt/e/Ciencia/noturno/2023-huang-compleasm
bash $R/data/prep_library.sh full
mkdir -p $R/runs/fullindex_attempt
bash $R/runs/run_one.sh fullindex_attempt GCF_000146045.2_R64 saccharomycetes_odb10
tail -15 $R/runs/fullindex_attempt/run.log
