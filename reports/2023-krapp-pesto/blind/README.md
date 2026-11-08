# Blind rerun

An independent reproduction of this paper, done by an agent that was not allowed to see the report
in the folder above, nor its scripts, its pre-registration or its adversarial review. It was given
the paper, the authors' repository address and the published numbers. It cloned the repository
again, rebuilt the dataset with its own reimplementation of `processing/build_dataset.py`, wrote its
own scoring code, pinned a different stack (torch 2.2.2, numpy 1.26.4, python 3.11, against the
first run's torch 1.11.0 and python 3.9) and froze its own pre-registration (`claims.json`, SHA-256
in `claims.json.sha256`) before downloading a single structure.

Both runs agree on every claim: median ROC AUC 0.9247 on the 53 MaSIF-site subunits against the
paper's 0.92, 0.9299 on the ScanNet-shared set against 0.93, 0.8002 for MaSIF-site itself against
0.80, and PeSTo best on 38 of 53. Both lost the same structure (1FSS_A) and found the same single
disagreement (4DX0_A).

This run added two things, both in the report above. It proved the 4DX0 explanation rather than
leaving it likely: scoring today's chain A against a label built only from the partner peptide of
the same model copy gives 0.909058 against the authors' 0.909057557582855, so the network output is
theirs and only the label moved when the assembly was redefined. And it found that the 53 prediction
files in the authors' `pdbs_test/` folder are not the paper's predictions and come from no released
checkpoint, which would mislead anyone who measured them.

Its own report carries one error, corrected in a note at the top of that file: it states the SPPIDER
and PSIVER per-residue predictions are missing from the repository. They are there, and the first
run scored them directly.

What is here: the pre-registration and its hash, the scripts, the per-structure outputs for both
sets, the Source Data extracted from the publisher's xlsx, and the run commands. The cached PDB
assemblies and the Python environment are not committed; `setup_env.sh` and the scripts fetch them.
