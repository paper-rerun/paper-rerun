#!/bin/bash
# Check that the score tables on GitHub (sources/analysis/data) are the same bytes as results/ in the Zenodo tarball
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
OUT=$ROOT/data/zenodo_extract
mkdir -p "$OUT"
date -u +%FT%TZ
nice -n 19 tar -xzf "$ROOT/data/zenodo/foldmason_data.tar.gz" -C "$OUT" \
	results/afdb_scores.tsv results/homstrad_scores.tsv results/afdb_families.tsv results/homstrad_families.tsv
for NAME in afdb_scores.tsv homstrad_scores.tsv afdb_families.tsv homstrad_families.tsv
do
	ZEN=$(md5sum "$OUT/results/$NAME" | cut -d' ' -f1)
	GIT=$(md5sum "$ROOT/sources/analysis/data/$NAME" | cut -d' ' -f1)
	if [ "$ZEN" = "$GIT" ]
	then
		echo "$NAME zenodo $ZEN github $GIT identical"
	else
		echo "$NAME zenodo $ZEN github $GIT DIFFERENT"
	fi
done
date -u +%FT%TZ
