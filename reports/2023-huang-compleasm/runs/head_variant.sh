#!/bin/bash
# Not graded: compleasm HEAD v0.2.10 with --odb odb10 on maize and yeast, separate library folder
ROOT=/mnt/e/Ciencia/noturno/2023-huang-compleasm
R=$ROOT/runs
until grep -q HSAP_RETRY_FINISHED $R/hsap_retry.log; do sleep 30; done
B=$ROOT/env/bin_head; mkdir -p $B
cp $ROOT/dl/v0210/compleasm_kit/{compleasm.py,_version.py,miniprot,hmmsearch} $B/; chmod +x $B/miniprot $B/hmmsearch
md5sum $B/* > $ROOT/env/kit_head_md5.txt
LIB=$ROOT/data/mb_downloads_head; mkdir -p $LIB/placement_files
cp $ROOT/data/file_versions.tsv $LIB/; touch $LIB/file_versions.tsv.done $LIB/placement_files.done $LIB/eukaryota_odb10.done
for L in liliopsida_odb10 saccharomycetes_odb10; do [ -d $LIB/$L ] || cp -r $ROOT/data/mb_downloads/$L $LIB/; touch $LIB/$L.done; done
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 MPLBACKEND=Agg
for X in "zmay GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0 liliopsida_odb10" "scer GCF_000146045.2_R64 saccharomycetes_odb10"; do
	set -- $X
	OUT=$R/head_$1; mkdir -p $OUT
	[ -s $OUT/summary.txt ] && continue
	echo "start $(date -Is) head_$1"
	( cd $OUT && /usr/bin/time -v -o $OUT/time.txt nice -n 19 $ROOT/env/.venv/bin/python $B/compleasm.py run -a $ROOT/data/genomes/$2_genomic.fna.gz -o $OUT -t 8 -l $3 --odb odb10 -L $LIB \
		--miniprot_execute_path $B/miniprot --hmmsearch_execute_path $B/hmmsearch > $OUT/run.log 2>&1 )
	echo "end $(date -Is) head_$1 rc=$?"
done
echo HEAD_FINISHED
