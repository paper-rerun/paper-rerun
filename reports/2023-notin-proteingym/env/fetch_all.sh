#!/bin/bash
# Resumable fetch of data + weights. Each file checked against the server Content-Length
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
fetch() # url dest
{
	local URL=$1 DEST=$2
	local EXPECTED=$(curl -sIL "$URL" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
	for TRY in 1 2 3 4 5; do
		local HAVE=$(stat -c %s "$DEST" 2>/dev/null || echo 0)
		if [ "$HAVE" = "$EXPECTED" ]; then echo "OK $DEST $HAVE"; return 0; fi
		curl -sSL --retry 5 -C - -o "$DEST" "$URL"
	done
	echo "FAIL $DEST have=$(stat -c %s "$DEST") expected=$EXPECTED"; return 1
}
B=https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3
fetch $B/DMS_ProteinGym_substitutions.zip $W/sources/DMS_ProteinGym_substitutions.zip
F=https://dl.fbaipublicfiles.com/fair-esm
mkdir -p $W/data/weights
for M in esm2_t6_8M_UR50D esm2_t12_35M_UR50D esm2_t30_150M_UR50D esm1b_t33_650M_UR50S esm2_t33_650M_UR50D; do
	fetch $F/models/$M.pt $W/data/weights/$M.pt
	fetch $F/regression/$M-contact-regression.pt $W/data/weights/$M-contact-regression.pt
done
fetch $B/zero_shot_substitutions_scores.zip $W/sources/zero_shot_substitutions_scores.zip
cd $W/data/weights && sha256sum *.pt > SHA256SUMS && cat SHA256SUMS
echo ALL_DONE
