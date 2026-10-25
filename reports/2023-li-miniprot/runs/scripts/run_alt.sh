#!/usr/bin/env bash
# Alternative readings from claims.json, run only after the main result is final.
# Never used for the verdict. Restartable: skips outputs that exist.
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-li-miniprot
BIN=$ROOT/env/bin
DATA=$ROOT/data
MAIN=$ROOT/runs/main
OUT=$ROOT/runs/alt
SETS=$ROOT/runs/testsets
REF=$ROOT/runs/ref
mkdir -p $OUT
export MPLBACKEND=Agg

HS_GENOME=$DATA/human/GRCh38.primary_assembly.genome.fa.gz
DM_GENOME=$DATA/fly/Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz
HS_GTF=$DATA/human/gencode.v41.annotation.gtf.gz
DM_GTF=$DATA/fly/Drosophila_melanogaster.BDGP6.32.107.gtf.gz

# Extra reference GTFs
for MODE in longest_spliced longest_cds_pc
do
	[ -s $REF/human.$MODE.gtf ] || python3 -I $ROOT/runs/scripts/reduce_gtf.py $MODE $HS_GTF $REF/human.$MODE.gtf
	[ -s $REF/fly.$MODE.gtf ] || python3 -I $ROOT/runs/scripts/reduce_gtf.py $MODE $DM_GTF $REF/fly.$MODE.gtf
done
for KIND in primary_assembly basic
do
	[ -s $REF/human_$KIND.longest_cds.gtf ] || python3 -I $ROOT/runs/scripts/reduce_gtf.py longest_cds $DATA/human/gencode.v41.$KIND.annotation.gtf.gz $REF/human_$KIND.longest_cds.gtf
done

junc()
{
	# label paf gtf flags...
	local LABEL=$1 PAF=$2 GTF=$3
	shift 3
	[ -s $OUT/$LABEL.junceval.txt ] || $BIN/k8 $BIN/paftools.js junceval -a "$@" $GTF $PAF > $OUT/$LABEL.junceval.txt
}
base()
{
	local LABEL=$1 PAF=$2 GTF=$3
	shift 3
	[ -s $OUT/$LABEL.exoneval.txt ] || $BIN/k8 $BIN/paftools.js exoneval -a -s "$@" $GTF $PAF > $OUT/$LABEL.exoneval.txt 2>/dev/null
}

for COL in zf_hs_j2 zf_hs_j1 mm_hs_j2 ag_dm_j2
do
	PAF=$MAIN/$COL.paf
	if [ $COL = ag_dm_j2 ]
	then
		JG=$DM_GTF; SP=fly
	else
		JG=$HS_GTF; SP=human
	fi
	# ALT-1: no -1
	junc $COL.ALT-1 $PAF $JG
	base $COL.ALT-1 $PAF $REF/$SP.longest_cds.gtf
	# ALT-3: -l 1 and -l 3
	junc $COL.ALT-3_l1 $PAF $JG -1 -l 1
	junc $COL.ALT-3_l3 $PAF $JG -1 -l 3
	# ALT-4: all CDS lines
	base $COL.ALT-4 $PAF $JG -1
	# ALT-5 and ALT-6
	base $COL.ALT-5 $PAF $REF/$SP.longest_spliced.gtf -1
	base $COL.ALT-6 $PAF $REF/$SP.longest_cds_pc.gtf -1
	if [ $SP = human ]
	then
		# ALT-2: -c with -1; ALT-1x2: -c without -1
		junc $COL.ALT-2 $PAF $JG -1 -c
		base $COL.ALT-2 $PAF $REF/human.longest_cds.gtf -1 -c
		junc $COL.ALT-1x2 $PAF $JG -c
		base $COL.ALT-1x2 $PAF $REF/human.longest_cds.gtf -c
		# ALT-7: other Gencode GTFs
		for KIND in primary_assembly basic
		do
			junc $COL.ALT-7_$KIND $PAF $DATA/human/gencode.v41.$KIND.annotation.gtf.gz -1
			base $COL.ALT-7_$KIND $PAF $REF/human_$KIND.longest_cds.gtf -1
		done
	fi
	echo "evaluated alt readings for $COL"
done

# Alternative test sets: new alignments, main evaluation definitions
align_and_eval()
{
	local LABEL=$1 OPTS=$2 GENOME=$3 QUERY=$4 JG=$5 BG=$6
	if [ ! -s $OUT/$LABEL.paf ]
	then
		echo "aligning $LABEL $(date)"
		/usr/bin/time -v -o $OUT/$LABEL.time $BIN/miniprot -t16 $OPTS $GENOME $QUERY > $OUT/$LABEL.paf.tmp 2> $OUT/$LABEL.miniprot.log
		mv $OUT/$LABEL.paf.tmp $OUT/$LABEL.paf
	fi
	junc $LABEL $OUT/$LABEL.paf $JG -1
	base $LABEL $OUT/$LABEL.paf $BG -1
}

for SET in zf_A_all zf_B1_plusMT zf_B2_noALT_allregions zf_C_pctranscript
do
	for J in j2 j1
	do
		align_and_eval zf_hs_$J.ALT-$SET -$J $HS_GENOME $SETS/alt/$SET.faa $HS_GTF $REF/human.longest_cds.gtf
	done
done
for SET in mm_A_longest_pc mm_B_canonical_pc
do
	align_and_eval mm_hs_j2.ALT-$SET -j2 $HS_GENOME $SETS/alt/$SET.faa $HS_GTF $REF/human.longest_cds.gtf
done

# ALT-T: mosquito with -t4, compare the PAF with the -t16 run
if [ ! -s $OUT/ag_dm_j2.ALT-T.paf ]
then
	$BIN/miniprot -t4 -j2 -G 50k $DM_GENOME $SETS/mosquito.longest.faa > $OUT/ag_dm_j2.ALT-T.paf.tmp 2> $OUT/ag_dm_j2.ALT-T.miniprot.log
	mv $OUT/ag_dm_j2.ALT-T.paf.tmp $OUT/ag_dm_j2.ALT-T.paf
fi
if cmp -s $OUT/ag_dm_j2.ALT-T.paf $MAIN/ag_dm_j2.paf
then
	echo "ALT-T: -t4 PAF identical to -t16" | tee $OUT/ALT-T.txt
else
	echo "ALT-T: -t4 PAF differs from -t16; sorted diff lines: $(diff <(sort $OUT/ag_dm_j2.ALT-T.paf) <(sort $MAIN/ag_dm_j2.paf) | grep -c '^[<>]')" | tee $OUT/ALT-T.txt
fi
echo "alt done $(date)"
