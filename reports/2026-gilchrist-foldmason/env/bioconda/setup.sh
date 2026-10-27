#!/bin/bash
# FoldMason 4-dd3c235 from bioconda (same release as the GitHub binary), micromamba env inside env/bioconda
set -euo pipefail
E=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/env/bioconda
SRC=/mnt/e/Ciencia/noturno/2023-shaw-skani/env/bin
export MAMBA_ROOT_PREFIX=$E/mamba
mkdir -p $E/bin
# Reuse the micromamba 2.0.5-0 binary of the skani folder, checked against its release sha256
if [ ! -x $E/bin/micromamba ]
then
	cp $SRC/micromamba $SRC/micromamba.sha256 $E/bin/
fi
echo "$(awk '{print $1}' $E/bin/micromamba.sha256)  $E/bin/micromamba" | sha256sum -c -
chmod +x $E/bin/micromamba
MM=$E/bin/micromamba
$MM --version
if [ ! -d $MAMBA_ROOT_PREFIX/envs/foldmason ]
then
	nice -n 19 $MM create -y -n foldmason -c conda-forge -c bioconda --strict-channel-priority --always-copy \
		"bioconda::foldmason=4.dd3c235=h5021889_0"
fi
$MM env export -n foldmason --explicit --md5 > $E/foldmason.explicit.txt
$MM list -n foldmason > $E/foldmason.list.txt
# md5 of the package archive in the local cache, to compare with anaconda.org (e902225dd97295d28e8fb30bd1ad034e)
md5sum $MAMBA_ROOT_PREFIX/pkgs/foldmason-4.dd3c235-h5021889_0.conda
sha256sum $MAMBA_ROOT_PREFIX/envs/foldmason/bin/foldmason
