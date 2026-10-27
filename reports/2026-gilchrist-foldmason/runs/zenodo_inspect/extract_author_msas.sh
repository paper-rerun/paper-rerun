#!/bin/bash
# Extract the authors' FoldMason default and fast MSAs for the AFDB clusters, and list which members each MSA holds
set -e
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
OUT=$ROOT/data/zenodo_extract
mkdir -p "$OUT"
nice -n 19 tar -xzf "$ROOT/data/zenodo/foldmason_data.tar.gz" -C "$OUT" --wildcards \
	'afdb_clusters/*/foldmason_aa.fa' 'afdb_clusters/*/foldmason_fast_aa.fa'
ls "$OUT/afdb_clusters" | wc -l
# Members per cluster in the authors' default MSA
for f in "$OUT"/afdb_clusters/*/foldmason_aa.fa
do
	printf "%s\t%s\n" "$(basename "$(dirname "$f")")" "$(grep '^>' "$f" | sed 's/^>//' | sort | tr '\n' ',')"
done > "$ROOT/runs/zenodo_inspect/author_msa_members.tsv"
head -2 "$ROOT/runs/zenodo_inspect/author_msa_members.tsv"
