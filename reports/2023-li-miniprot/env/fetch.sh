#!/usr/bin/env bash
# Download tools and data, check each file against the server size only.
# Checksums (md5, BSD sum, sha256) are checked in setup.sh, which calls this script first.
# Restartable: a file already present with the server size is not fetched again.
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-li-miniprot
LOG=$ROOT/runs/logs/fetch.log
mkdir -p $ROOT/runs/logs $ROOT/env/dl $ROOT/data/{human,mouse,zebrafish,fly,mosquito}
# Send curl errors to the log too, an earlier run died without leaving a trace
exec 2>>$LOG
echo "fetch start $(date -Is)" >> $LOG

GC_H=https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_41
GC_M=https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M30
E107=https://ftp.ensembl.org/pub/release-107
EM54=https://ftp.ensemblgenomes.ebi.ac.uk/pub/metazoa/release-54

# dest_dir url
LIST="
env/dl https://github.com/lh3/miniprot/releases/download/v0.7/miniprot-0.7_x64-linux.tar.bz2
env/dl https://github.com/lh3/miniprot/releases/download/v0.7/miniprot-0.7.tar.bz2
env/dl https://zenodo.org/records/11357203/files/k8-1.2.tar.bz2
env/dl https://raw.githubusercontent.com/lh3/minimap2/822ccd173358f11842b6dc54e17bbdcc2d9a0a9a/misc/paftools.js
data/human $GC_H/MD5SUMS
data/human $GC_H/GRCh38.primary_assembly.genome.fa.gz
data/human $GC_H/gencode.v41.annotation.gtf.gz
data/human $GC_H/gencode.v41.primary_assembly.annotation.gtf.gz
data/human $GC_H/gencode.v41.basic.annotation.gtf.gz
data/mouse $GC_M/MD5SUMS
data/mouse $GC_M/gencode.vM30.pc_translations.fa.gz
data/mouse $GC_M/gencode.vM30.annotation.gtf.gz
data/zebrafish $E107/fasta/danio_rerio/pep/CHECKSUMS
data/zebrafish $E107/fasta/danio_rerio/pep/Danio_rerio.GRCz11.pep.all.fa.gz
data/fly $E107/fasta/drosophila_melanogaster/dna/Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz
data/fly $E107/gtf/drosophila_melanogaster/Drosophila_melanogaster.BDGP6.32.107.gtf.gz
data/mosquito $EM54/fasta/anopheles_gambiae/pep/CHECKSUMS
data/mosquito $EM54/fasta/anopheles_gambiae/pep/Anopheles_gambiae.AgamP4.pep.all.fa.gz
"
# The two fly CHECKSUMS live in different directories, fetch them under distinct names
curl -sSfL -o $ROOT/data/fly/CHECKSUMS.dna $E107/fasta/drosophila_melanogaster/dna/CHECKSUMS
curl -sSfL -o $ROOT/data/fly/CHECKSUMS.gtf $E107/gtf/drosophila_melanogaster/CHECKSUMS

echo "$LIST" | while read -r DIR URL
do
	[ -z "${DIR:-}" ] && continue
	FILE=$ROOT/$DIR/$(basename "$URL")
	SERVER_SIZE=$(curl -sSIL "$URL" | tr -d '\r' | awk 'tolower($1)=="content-length:"{s=$2} END{print s}')
	if [ -f "$FILE" ] && [ "$(stat -c %s "$FILE")" = "$SERVER_SIZE" ]
	then
		echo "skip $FILE ($SERVER_SIZE)" | tee -a $LOG
		continue
	fi
	curl -sSfL --retry 5 -C - -o "$FILE" "$URL" || curl -sSfL --retry 5 -o "$FILE" "$URL"
	LOCAL_SIZE=$(stat -c %s "$FILE")
	echo "got $FILE local=$LOCAL_SIZE server=$SERVER_SIZE" | tee -a $LOG
	if [ "$LOCAL_SIZE" != "$SERVER_SIZE" ]
	then
		echo "SIZE MISMATCH $FILE" | tee -a $LOG
		exit 1
	fi
done
echo "downloads done" | tee -a $LOG
