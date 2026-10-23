#!/usr/bin/env bash
# Working env for the ACT DR6 lensing reproduction (run inside WSL Ubuntu 24.04)
# Pins the versions the authors' chains were made with: CAMB 1.3.6 and Cobaya 3.2.2
# (see the updated.yaml of their public chains). Current CAMB (2.0.5) drops the
# lens_margin argument and every Cobaya run of this likelihood fails, see REPORT.md
set -euo pipefail
D=/mnt/e/Ciencia/artigos/2024-madhavacheril-act-dr6
cd $D
export PATH=$HOME/.local/bin:$PATH

# System deps: MPI for parallel chains, gfortran to build CAMB 1.3.6, aria2 for the data
sudo apt-get install -y openmpi-bin libopenmpi-dev gfortran aria2

uv venv --python 3.11 .venv-pinned
source .venv-pinned/bin/activate
# CAMB 1.3.6 imports pkg_resources at build time, so setuptools has to be old
uv pip install "numpy<2" "scipy<1.12" "setuptools<70" wheel "flit_core>=3.2,<4"
uv pip install --no-build-isolation "camb==1.3.6" "cobaya==3.2.2" "getdist<1.5" mpi4py pytest tqdm requests -e ./repo
# Exact versions that worked are in env/requirements-pinned.lock.txt
# NOTE: that venv pulled pandas 3.0.6. The lens-only MCMC ran on it fine (chain weights checked),
# but Cobaya 3.2.2's BAO likelihoods crash on pandas 3 (assert has_type, string dtype is no longer
# object). The BAO reweighting and the lensing+BAO MCMC used .venv-post, same pins plus:
#   uv pip install "pandas<2.1"      (got 2.0.3)
# For a fresh setup just add "pandas<2.1" to the line above

# Likelihood data (361 MB). LAMBDA gives ~200 KB/s per connection, so 16 connections
mkdir -p /tmp/actdl && cd /tmp/actdl
aria2c -x 16 -s 16 https://lambda.gsfc.nasa.gov/data/suborbital/ACT/ACT_dr6/likelihood/data/ACT_dr6_likelihood_v1.2.tgz
# sha256 we got: bbcde3bcacd7c9a97138c4873c8a1217635a18504d15c4f86b1fba39d3601085
# Cobaya 3.6 refuses the likelihood unless the data sit in a packages path,
# so unpack there too (the in-repo data/ copy is what the plain Python API reads)
mkdir -p $D/packages/data/ACT_dr6_likelihood
tar -zxf ACT_dr6_likelihood_v1.2.tgz -C $D/packages/data/ACT_dr6_likelihood
mkdir -p $D/repo/act_dr6_lenslike/data
tar -zxf ACT_dr6_likelihood_v1.2.tgz -C $D/repo/act_dr6_lenslike/data

# BAO data for the lensing+BAO run
cd $D
cobaya-install bao.sdss_dr7_mgs bao.sixdf_2011_bao bao.sdss_dr12_lrg_bao_dmdh bao.sdss_dr16_lrg_bao_dmdh -p $D/packages
