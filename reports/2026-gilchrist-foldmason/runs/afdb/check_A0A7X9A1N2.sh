#!/bin/bash
# The one complete cluster that does not match to 1e-6: A0A7X9A1N2
# 1) rerun it twice from scratch to see if FoldMason is deterministic here
# 2) score the authors' published MSAs on our structure DB, to separate alignment from coordinates/scoring
ROOT=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason
FM=$ROOT/env/bioconda/mamba/envs/foldmason/bin/foldmason
C=A0A7X9A1N2
PDB=$ROOT/data/afdb_clusters/$C/pdbs
W=$ROOT/runs/afdb/check_$C
rm -rf "$W"; mkdir -p "$W"
for R in 1 2
do
	nice -n 19 "$FM" easy-msa "$PDB" "$W/r$R" "$W/r${R}_tmp" --threads 1 > "$W/r$R.log" 2>&1
	nice -n 19 "$FM" easy-msa "$PDB" "$W/r${R}_fast" "$W/r${R}_fast_tmp" --threads 1 --fast > "$W/r${R}_fast.log" 2>&1
done
echo "md5 of MSAs (main run, rerun 1, rerun 2):"
md5sum $ROOT/runs/afdb/out/$C/foldmason_aa.fa "$W/r1_aa.fa" "$W/r2_aa.fa"
md5sum $ROOT/runs/afdb/out/$C/foldmason_fast_aa.fa "$W/r1_fast_aa.fa" "$W/r2_fast_aa.fa"
# Authors' MSAs scored on the structure DB of our default run
DB=$ROOT/runs/afdb/out/$C/foldmason_tmp/latest/structures
for T in foldmason foldmason_fast
do
	mkdir -p "$W/authors"
	nice -n 19 "$FM" msa2lddtreport "$DB" "$ROOT/data/zenodo_extract/afdb_clusters/$C/${T}_aa.fa" "$W/authors/$T.html" --threads 1 > "$W/authors/${T}_lddt.log" 2>&1
	echo "authors' $T MSA on our structures: $(awk -f $ROOT/sources/analysis/extractLDDT.awk "$W/authors/$T.html" | awk '$3=="lddt"{print $4}')"
done
# Same residues aligned? Compare the ungapped sequences and the gap patterns
python3 -I - "$ROOT/runs/afdb/out/$C/foldmason_aa.fa" "$ROOT/data/zenodo_extract/afdb_clusters/$C/foldmason_aa.fa" <<'PY'
import sys
def read(p):
	d, k = {}, None
	for l in open(p):
		l = l.strip()
		if l.startswith(">"): k = l[1:].split()[0]; d[k] = ""
		elif k: d[k] += l
	return d
a, b = read(sys.argv[1]), read(sys.argv[2])
print("members ours/authors", len(a), len(b), "same names", set(a) == set(b))
print("same ungapped sequences", all(a[k].replace("-", "") == b[k].replace("-", "") for k in a if k in b))
print("identical aligned rows", sum(a[k] == b[k] for k in a if k in b), "of", len(a), "; MSA length ours/authors", len(next(iter(a.values()))), len(next(iter(b.values()))))
PY
