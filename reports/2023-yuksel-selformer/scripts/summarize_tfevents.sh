#!/bin/bash
# What the authors' own fine-tuning logs say, per published model folder
set -u
B=/mnt/e/Ciencia/noturno/2023-yuksel-selformer
cd "$B"
for t in bbbp bace sider tox21; do
	d="data/extracted/classification_models/SELFormer_${t}_scaffold_optimized"
	[ -d "$d" ] || continue
	echo "===== $t"
	python3 -I scripts/read_tfevents.py "$d/runs/**/events.out.tfevents*" > "runs/logs/tfevents_${t}.log" 2>&1
	echo "scalar tags:"
	grep -o "] *[a-z/_-]*=" "runs/logs/tfevents_${t}.log" 2>/dev/null | sort -u | head
	sed -E 's/.* ([a-z/_-]+)=.*/\1/' "runs/logs/tfevents_${t}.log" | grep -v '^#' | sort | uniq -c | sort -rn | head
	for tag in "eval/roc-auc" "eval/prc-auc" "eval/accuracy" "eval/f1" "eval/loss"; do
		vals=$(grep -F "$tag=" "runs/logs/tfevents_${t}.log" | sed -E 's/.*=//')
		[ -n "$vals" ] || continue
		echo "$tag: n=$(echo "$vals" | wc -l) max=$(echo "$vals" | sort -g | tail -1) min=$(echo "$vals" | sort -g | head -1) last=$(echo "$vals" | tail -1)"
	done
done
