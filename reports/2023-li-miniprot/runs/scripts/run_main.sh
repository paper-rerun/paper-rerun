#!/usr/bin/env bash
# Main pre-registered run: build test sets and reference GTFs, align the four columns, evaluate.
# Restartable: every step skips outputs that already exist.
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-li-miniprot
BIN=$ROOT/env/bin
DATA=$ROOT/data
OUT=$ROOT/runs/main
SETS=$ROOT/runs/testsets
REF=$ROOT/runs/ref
mkdir -p $OUT $SETS $REF $ROOT/runs/logs
export MPLBACKEND=Agg

$BIN/miniprot --version

# The GRCh38 index needs ~22 GB (paper: 21.8 and 22.5 GB peak), so log what WSL gives us before indexing
{
	echo "memory check $(date -Is)"
	if [ -f /mnt/c/Users/tessa/.wslconfig ]
	then
		echo ".wslconfig:"; cat /mnt/c/Users/tessa/.wslconfig
	else
		echo "no .wslconfig, WSL default memory limit"
	fi
	grep -E "MemTotal|MemAvailable|SwapTotal" /proc/meminfo
	free -g
} | tee -a $ROOT/runs/logs/setup.log $ROOT/runs/logs/memory.log

# Test sets
if [ ! -s $SETS/mouse.testset.faa ]
then
	python3 -I $ROOT/runs/scripts/testsets.py $DATA $SETS > $ROOT/runs/logs/testsets.log
fi
cat $ROOT/runs/logs/testsets.log

# Longest-transcript CDS references for base Sn/Sp
[ -s $REF/human.longest_cds.gtf ] || python3 -I $ROOT/runs/scripts/reduce_gtf.py longest_cds $DATA/human/gencode.v41.annotation.gtf.gz $REF/human.longest_cds.gtf
[ -s $REF/fly.longest_cds.gtf ] || python3 -I $ROOT/runs/scripts/reduce_gtf.py longest_cds $DATA/fly/Drosophila_melanogaster.BDGP6.32.107.gtf.gz $REF/fly.longest_cds.gtf

HS_GENOME=$DATA/human/GRCh38.primary_assembly.genome.fa.gz
DM_GENOME=$DATA/fly/Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz
HS_GTF=$DATA/human/gencode.v41.annotation.gtf.gz
DM_GTF=$DATA/fly/Drosophila_melanogaster.BDGP6.32.107.gtf.gz

# column  options  genome  query  junc_gtf  base_gtf
COLUMNS="
zf_hs_j2|-j2|$HS_GENOME|$SETS/zebrafish.longest.faa|$HS_GTF|$REF/human.longest_cds.gtf
zf_hs_j1|-j1|$HS_GENOME|$SETS/zebrafish.longest.faa|$HS_GTF|$REF/human.longest_cds.gtf
mm_hs_j2|-j2|$HS_GENOME|$SETS/mouse.testset.faa|$HS_GTF|$REF/human.longest_cds.gtf
ag_dm_j2|-j2 -G 50k|$DM_GENOME|$SETS/mosquito.longest.faa|$DM_GTF|$REF/fly.longest_cds.gtf
"

echo "$COLUMNS" | while IFS='|' read -r NAME OPTS GENOME QUERY JUNC_GTF BASE_GTF
do
	[ -z "$NAME" ] && continue
	if [ ! -s $OUT/$NAME.paf ]
	then
		echo "aligning $NAME $(date)"
		/usr/bin/time -v -o $OUT/$NAME.time $BIN/miniprot -t16 $OPTS $GENOME $QUERY > $OUT/$NAME.paf.tmp 2> $OUT/$NAME.miniprot.log
		mv $OUT/$NAME.paf.tmp $OUT/$NAME.paf
	fi
	if [ ! -s $OUT/$NAME.junceval.txt ]
	then
		$BIN/k8 $BIN/paftools.js junceval -a -1 $JUNC_GTF $OUT/$NAME.paf > $OUT/$NAME.junceval.txt
	fi
	if [ ! -s $OUT/$NAME.exoneval.txt ]
	then
		$BIN/k8 $BIN/paftools.js exoneval -a -s -1 $BASE_GTF $OUT/$NAME.paf > $OUT/$NAME.exoneval.txt 2> $OUT/$NAME.exoneval.log
	fi
	echo "== $NAME"; cat $OUT/$NAME.junceval.txt $OUT/$NAME.exoneval.txt
done
echo "main done $(date)"
