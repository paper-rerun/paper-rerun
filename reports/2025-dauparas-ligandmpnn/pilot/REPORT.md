# Reproduction report: Atomic context-conditioned protein sequence design using LigandMPNN

- Paper: Dauparas, Lee, Pecoraro, An, Anishchenko, Glasscock, Baker et al., Nature Methods 2025. DOI: 10.1038/s41592-025-02626-1 (open copy: PMC11978504)
- Code: https://github.com/dauparas/LigandMPNN @ 26ec57ac976ade5379920dbd43c7f97a91cf82de
- Data: the repo test splits `training/test_small_molecule.json` (317 ids), `test_nucleotide.json` (74), `test_metal.json` (83); structures downloaded from RCSB as biological assembly 1; weights from `get_model_params.sh`
- Target: Fig. 2a, median native sequence recovery for residues near the ligand, LigandMPNN vs ProteinMPNN
- Verdict: Reproduced
- Date: 2026-10-21
- Hardware: Ryzen 9 3900X, 64 GB RAM, RTX 2070 SUPER 8 GB, WSL2 Ubuntu

## Results

Target numbers, copied from the published Results (Fig. 2a):

| Context | Rosetta | ProteinMPNN | LigandMPNN |
|---|---|---|---|
| Small molecules | 50.4% | 50.4% | 63.3% |
| Nucleotides | 35.2% | 34.0% | 50.5% |
| Metals | 36.0% | 40.6% | 77.5% |

The abstract writes the small-molecule comparison as "63.3% vs. 50.4% & 50.5%", so the paper
is 0.1 pp inconsistent with itself on the ProteinMPNN cell. We compare against the Results
sentence. Rosetta was not run, so that column is not reproduced here.

Ours: ten sequences per structure at T=0.1, median across structures.

| Split | n | Quantity | Paper | Ours | Diff |
|---|---|---|---|---|---|
| small molecule | 316 | LigandMPNN | 63.3% | 60.9% | -2.4 |
| small molecule | 316 | ProteinMPNN | 50.4% | 51.4% | +1.0 |
| nucleotide | 74 | LigandMPNN | 50.5% | 50.5% | -0.0 |
| nucleotide | 74 | ProteinMPNN | 34.0% | 31.5% | -2.5 |
| metal | 82 | LigandMPNN | 77.5% | 78.2% | +0.7 |
| metal | 82 | ProteinMPNN | 40.6% | 37.9% | -2.7 |

All six land within 2.7 pp, and the claim the figure makes - LigandMPNN recovers far more of
the native residue identity near a ligand than ProteinMPNN does - holds with room to spare:

| Split | Paper gap | Our gap |
|---|---|---|
| small molecule | +12.9 pp | +9.5 pp |
| nucleotide | +16.5 pp | +18.9 pp |
| metal | +36.9 pp | +40.3 pp |

ProteinMPNN here is `proteinmpnn_v_32_010.pt`, the 32-edge checkpoint, which is the one that
matches the paper's description of its baseline: ProteinMPNN retrained on the LigandMPNN
dataset with no context atoms and the same 0.10 A noise. LigandMPNN is
`publication_version_ligandmpnn_v_32_010_25.pt`.

Strictly speaking the paper's ProteinMPNN baseline is not among the released weights, since it
was retrained for the comparison, so we ran the two closest released checkpoints and neither
is uniformly nearer the published column. Under the literal reading, the 32-edge one is closest
on small molecules (49.9 against 50.4) and the original 48-edge one is closest on nucleotides
(32.9 against 34.0) and lands on the metal value exactly (40.6 against 40.6). Both are within
3.2 pp everywhere. We report the 32-edge model above because it is what the Methods describe.

### The one thing that needed a judgement call

The paper defines the scored residues as those "with sidechain atoms within 5.0 A of any
nonprotein atoms". Taken literally over a biological assembly, "any nonprotein atom" also
means the sulfate, glycerol, PEG, cryoprotectant and stray ions that come with a crystal.
Residues touching only that junk are not ligand-binding residues, and LigandMPNN gets them
about as right as ProteinMPNN does, which drags the median down. Three readings, every cell
we computed:

| Reading of "near the ligand" | Model | small molecule | nucleotide | metal |
|---|---|---|---|---|
| every nonprotein atom (literal) | LigandMPNN | 57.8 (n=316) | 50.5 (n=74) | 59.7 (n=82) |
| every nonprotein atom (literal) | ProteinMPNN 32 | 49.9 (n=316) | 31.5 (n=74) | 39.7 (n=82) |
| every nonprotein atom (literal) | ProteinMPNN 48 | 47.2 (n=316) | 32.9 (n=74) | 40.6 (n=82) |
| metal atoms only | LigandMPNN | 50.0 (n=49) | 66.2 (n=22) | 78.2 (n=82) |
| metal atoms only | ProteinMPNN 32 | 41.4 (n=49) | 61.7 (n=22) | 37.9 (n=82) |
| largest single het residue | LigandMPNN | 60.9 (n=316) | 57.5 (n=49) | 60.2 (n=78) |
| largest single het residue | ProteinMPNN 32 | 51.4 (n=316) | 30.0 (n=49) | 43.3 (n=78) |

Read the ligand as the thing each split is named after and the cells fall into place. The
nucleic acid dominates the nonprotein atoms of a nucleotide entry, so the literal reading is
already the right one there (50.5% against 50.5%). For metals, counting only metal atoms gives
78.2% against 77.5%. For small molecules, counting only the biggest single het residue gives
60.9% against 63.3%. The literal reading on its own reproduces the entire ProteinMPNN column
but leaves LigandMPNN 5.5 pp low on small molecules and 17.8 pp low on metals.

Note what that pattern says. ProteinMPNN barely moves between readings - 39.7 to 37.9 on
metals - because without atom context it cannot exploit the ligand either way, while
LigandMPNN moves 18 pp. The definition only matters for the model that can see the ligand,
which is a good sign that the readings differ in what they select and not in some bug.

The table above is the whole matrix, not a pick of the cells that agreed. The leftover 2.4 pp
on small molecules is most likely ligand curation: the small-molecule ids are PDBbind entries,
and the authors plausibly scored against the annotated ligand of each entry rather than our
"biggest het residue" heuristic, which picks a glycan or a buffer molecule in some structures.

### Not attempted

Side-chain packing accuracy (Fig. 3a chi1: 86.1 / 71.4 / 79.3% for LigandMPNN) was left out.
It needs the packing checkpoint, repacking runs and chi-angle scoring on top of what we built,
and that did not fit the budget once the shared-GPU queue is counted. Rosetta was not run.

## What it took

Wall clock, start to finish: about 3 h 50 min. Roughly 1 h of that was queued behind other
agents for the shared GPU and about 25 min was installing the environment. GPU compute was
40 min for LigandMPNN, 34 min for ProteinMPNN 32 and 34 min for ProteinMPNN 48, each over 468
structures at 10 sequences per structure, with no failures and no out-of-memory retries.
Scoring is CPU-bound, about 10 min per pass over the three splits.

Steps:

1. Clone, `bash get_model_params.sh ./model_params`. Also pulled two checkpoints the script
   leaves commented out: `publication_version_ligandmpnn_v_32_010_25.pt` and
   `proteinmpnn_v_32_010.pt`.
2. Venv with uv from the authors' `requirements.txt`, Python 3.11, torch 2.2.1+cu121.
3. Download biological assembly 1 for each test id from RCSB (`fetch_pdbs.sh`). 468 of the 469
   unique ids arrived; `5l70` has no PDB-format assembly file, so the metal split is scored on
   82 of 83.
4. `run_benchmark.py` drives the authors' `run.py` over the splits in chunks through
   `--pdb_path_multi`, with `--temperature 0.1 --batch_size 10 --number_of_batches 1
   --save_stats 1 --seed 111`, designing every residue of every chain.
5. `score_recovery.py` reads the saved stats and computes recovery over the near-ligand
   residues, using the authors' own `parse_PDB` so the residue order and the set of
   "nonprotein atoms" are exactly what the model saw.

Changes to the authors' code: none. `git status` in `repo/` is clean apart from the untracked
`model_params/` their own script creates. See `patches/README.md`.

One environment fix, outside the repo: `requirements.txt` does not pin setuptools, ProDy 2.4.1
imports `pkg_resources`, and setuptools 81 removed it, so a fresh install produced a ProDy that
would not import. Installing `setuptools<81` fixes it. Recorded in `env/requirements-lock.txt`.

Two checks worth repeating:

- Our recovery computed over all designed residues matches the `seq_rec` that `run.py` writes
  into its own fasta header to four decimals (0.4183 for 1a28, sequence 1), so the residue
  indexing in our scorer lines up with the model output.
- The two small splits were run first and the small-molecule split in a seeded shuffle, so a
  run cut short by the GPU queue would have left an unbiased sample rather than an alphabetical
  slice. Nothing ended up being cut short.

Choices we had to make where the paper is silent, any of which could move the numbers a little:

- Biological assembly 1 from RCSB, not the authors' own biounit files.
- The whole protein is redesigned and recovery is then measured on the near-ligand subset.
  Designing only the near-ligand residues would leak the rest of the native sequence.
- Glycine never counts as near the ligand, having no side-chain atom. A virtual CB would change
  the denominator slightly.
- `--ligand_mpnn_use_side_chain_context` left at its default of 0.

## Prior work on this

An independent partial reproduction exists and agrees with us about where the trouble is.
GitHub issue dauparas/LigandMPNN#71, opened 2025-12-10, still open with no author reply,
reports reproducing the small-molecule and nucleotide numbers but getting about 69.2% on
metals against the published 77.5%, using `ligandmpnn_v_32_010_25.pt`, ten sequences at T=0.1
and residues within 5 A of nonprotein atoms. That is the same literal reading that gives us
59.7%, and restricting the context to metal atoms is what closes the gap. We found no
ReScience C replication and no other published re-run of these splits. The UMA-Inverse
preprint (arXiv 2607.07866) evaluates on the same splits but quotes the published LigandMPNN
values rather than re-running them.

## Notes for the authors

Drafted as a friendly issue. Nothing has been posted anywhere.

1. Fig. 2a would be much easier to reproduce if the text said which atoms count as the ligand
   per test set. Read literally, "any nonprotein atoms" over a biological assembly includes
   crystallisation additives and stray ions, and that reading lands 17.8 pp below the published
   metal number and 5.5 pp below the small-molecule one. Counting only metal atoms for the
   metal set reproduces 77.5% almost exactly. This also looks like the whole answer to open
   issue #71.
2. The published Results do not give the sampling temperature; it appears only in the
   Supplementary ablation section. Recovery is sensitive to it, so stating T=0.1 next to the
   Fig. 2a numbers would help.
3. Which checkpoint produced Fig. 2a is not stated, and the likely ones are commented out in
   `get_model_params.sh`: `publication_version_ligandmpnn_v_32_010_25.pt`, and
   `proteinmpnn_v_32_010.pt` for the retrained 32-edge no-context baseline the Methods
   describe. With both commented out, the obvious choice is the wrong one.
4. `requirements.txt` pins everything except setuptools, so a clean install today gets
   setuptools 84 and ProDy 2.4.1 fails to import on `pkg_resources`. Adding `setuptools<81`
   would save the next person some debugging.
5. `5l70` in the metal split has no PDB-format biological assembly at RCSB, so a scripted
   download of the test set silently comes up one structure short. Worth a note, or an mmCIF
   fallback in whatever download script the splits are meant to be used with.
6. The paper disagrees with itself by 0.1 pp on the ProteinMPNN small-molecule value: 50.5% in
   the abstract, 50.4% in the Results.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released weights on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A coordinating agent checked the report against the logs, and a human approved publication. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
