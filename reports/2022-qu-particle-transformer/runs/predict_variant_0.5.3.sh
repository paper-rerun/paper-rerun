#!/bin/bash
# Variant D10: weaver-core 0.5.3, num-workers 0 (weaver-core issue 14). Run weaver --predict per class group, skip groups already done (restartable)
# Usage: predict.sh <ParT|PN> <fp32|amp> <outdir> <test_dir> [file_glob_suffix]
#   file_glob_suffix defaults to "_*.root" (all files); pilot uses "_100.root" style
set -u
MODEL=$1
PREC=$2
OUT=$3
TESTDIR=$4
SUFFIX=${5:-_*.root}
HERE=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
PY=$HERE/env/.venv/bin/python
export MPLBACKEND=Agg
cd $HERE/repo

if [[ "$MODEL" == "ParT" ]]; then
	NET=networks/example_ParticleTransformer.py
	CKPT=$HERE/data/weights/ParT_full.pt
else
	NET=networks/example_ParticleNet.py
	CKPT=$HERE/data/weights/ParticleNet_full.pt
fi
AMP=""
[[ "$PREC" == "amp" ]] && AMP="--use-amp"

mkdir -p $OUT
for GROUP in HToBB HToCC HToGG HToWW2Q1L HToWW4Q TTBar TTBarLep WToQQ ZToQQ ZJetsToNuNu
do
	# Skip groups that already finished
	if [ -f $OUT/pred_$GROUP.root ]; then
		echo "skip $GROUP"
		continue
	fi
	# GPU lock only around the weaver call
	flock /mnt/e/Ciencia/.gpu.lock $HERE/env/.venv-0.5.3/bin/weaver --predict \
		--data-test "$GROUP:$TESTDIR/${GROUP}${SUFFIX}" \
		--data-config data/JetClass/JetClass_full.yaml \
		--network-config $NET $AMP \
		--model-prefix $CKPT \
		--gpus 0 --batch-size 512 --num-workers 0 \
		--predict-output $OUT/tmp_pred.root \
		--log $OUT/weaver_$GROUP.log
	# weaver names the file tmp_pred_<group>.root; rename only when it exists, so a crash leaves no output
	if [ -f $OUT/tmp_pred_$GROUP.root ]; then
		mv $OUT/tmp_pred_$GROUP.root $OUT/pred_$GROUP.root
	else
		echo "FAILED $GROUP"
		exit 1
	fi
done
echo "all groups done"
