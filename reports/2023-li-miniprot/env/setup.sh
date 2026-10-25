#!/usr/bin/env bash
# Rebuild the environment: fetch (fetch.sh), verify checksums, unpack binaries into env/bin.
# Checks every file against env/lock.sha256 when that file exists.
set -euo pipefail
ROOT=/mnt/e/Ciencia/noturno/2023-li-miniprot
ENV=$ROOT/env
LOG=$ROOT/runs/logs/setup.log
mkdir -p $ENV/bin $ROOT/runs/logs
: > $LOG

[ "${SKIP_FETCH:-0}" = "1" ] || bash $ENV/fetch.sh

# Published checksums: k8 on Zenodo (md5), Gencode MD5SUMS, Ensembl CHECKSUMS (BSD sum)
echo "b187073930687c4b5559998153270a08  $ENV/dl/k8-1.2.tar.bz2" | md5sum -c - | tee -a $LOG
# paftools.js at r1152 must match the copy the claims agent read
echo "2e85a21498c057cb1b617cbd908b2a55e9eae4ffb116aa9991c58ea2bb052206  $ENV/dl/paftools.js" | sha256sum -c - | tee -a $LOG

for SET in human mouse
do
	for FILE in $ROOT/data/$SET/*.gz
	do
		NAME=$(basename $FILE)
		WANT=$(awk -v n=$NAME '$2==n{print $1}' $ROOT/data/$SET/MD5SUMS)
		GOT=$(md5sum $FILE | cut -d' ' -f1)
		[ "$WANT" = "$GOT" ] && echo "md5 OK $NAME" | tee -a $LOG || { echo "md5 FAIL $NAME want=$WANT got=$GOT" | tee -a $LOG; exit 1; }
	done
done

ensembl_check()
{
	# CHECKSUMS lines: "<sum> <blocks> <filename>"
	local FILE=$1 SUMS=$2
	local NAME=$(basename $FILE)
	local WANT=$(awk -v n=$NAME '$3==n{print $1" "$2}' $SUMS)
	local GOT=$(sum $FILE | awk '{print $1" "$2}')
	[ "$WANT" = "$GOT" ] && echo "sum OK $NAME" | tee -a $LOG || { echo "sum FAIL $NAME want=$WANT got=$GOT" | tee -a $LOG; exit 1; }
}
ensembl_check $ROOT/data/zebrafish/Danio_rerio.GRCz11.pep.all.fa.gz $ROOT/data/zebrafish/CHECKSUMS
ensembl_check $ROOT/data/mosquito/Anopheles_gambiae.AgamP4.pep.all.fa.gz $ROOT/data/mosquito/CHECKSUMS
ensembl_check $ROOT/data/fly/Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz $ROOT/data/fly/CHECKSUMS.dna
ensembl_check $ROOT/data/fly/Drosophila_melanogaster.BDGP6.32.107.gtf.gz $ROOT/data/fly/CHECKSUMS.gtf

# Unpack: prebuilt miniprot 0.7 and k8 1.2 (Linux x86_64 binary inside the tarball)
tar -xjf $ENV/dl/miniprot-0.7_x64-linux.tar.bz2 -C $ENV/dl
cp $ENV/dl/miniprot-0.7_x64-linux/miniprot $ENV/bin/miniprot
tar -xjf $ENV/dl/k8-1.2.tar.bz2 -C $ENV/dl
cp $ENV/dl/k8-1.2/k8-x86_64-Linux $ENV/bin/k8
cp $ENV/dl/paftools.js $ENV/bin/paftools.js
chmod +x $ENV/bin/miniprot $ENV/bin/k8

$ENV/bin/miniprot --version | tee -a $LOG
$ENV/bin/k8 -v | tee -a $LOG || true
$ENV/bin/k8 $ENV/bin/paftools.js version | tee -a $LOG

# Freeze or check the lock
cd $ROOT
FILES="env/bin/miniprot env/bin/k8 env/bin/paftools.js $(ls data/*/*.gz)"
if [ -f $ENV/lock.sha256 ]
then
	sha256sum -c $ENV/lock.sha256 | tee -a $LOG
else
	sha256sum $FILES > $ENV/lock.sha256
	echo "wrote lock.sha256" | tee -a $LOG
fi
