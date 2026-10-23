# Target numbers copied from the paper

Published version: Dauparas et al., "Atomic context-conditioned protein sequence design
using LigandMPNN", Nature Methods 22, 717-723 (2025). DOI 10.1038/s41592-025-02626-1.
The Nature page is behind a login, so the numbers below were read off the author-accessible
full text of the same manuscript (bioRxiv 2023.12.22.573103, Results and Fig. 2a), whose
abstract sentence matches the published abstract verbatim.

## Fig. 2a - median native sequence recovery, residues near the ligand

| Context | Rosetta | ProteinMPNN | LigandMPNN |
|---|---|---|---|
| Small molecules | 50.4% | 50.4% | 63.3% |
| Nucleotides | 35.2% | 34.0% | 50.5% |
| Metals | 36.0% | 40.6% | 77.5% |

The paper disagrees with itself by 0.1 pp on one cell: the abstract writes the small-molecule
comparison as "63.3% vs. 50.4% & 50.5%", the Results sentence gives ProteinMPNN as 50.4%.

## Definitions and settings, quoted

- "We report native sequence recovery for residues that are close to the ligand, having
  side-chain atoms within 5.0 A of any non-protein atoms."
- "The median sequence recoveries (ten designed sequences per protein) ..."
- "Sequence recoveries are averaged over the residues within 5.0 A from the context atoms."
  (Fig. 2 caption. Caption says averaged, Results says median - the Results sentence is the
  source of the numbers above.)
- "all sequences were designed using the sampling temperature of 0.1."
- "we retrained ProteinMPNN on the same training dataset of PDB biounits as LigandMPNN,
  except none of the context atoms were provided during training."
- LigandMPNN baseline: 0.1 A Gaussian noise, 25 context atoms per residue, 2% of side chains
  randomly given as context during training.
- Test sets: 317 small molecule, 74 nucleic acid, 83 metal structures. The repo's
  training/test_*.json files hold exactly 317 / 74 / 83 ids, so the splits match.

## Chi1 side-chain packing (Fig. 3a), not attempted here

| Context | Rosetta | ProteinMPNN | LigandMPNN |
|---|---|---|---|
| Small molecules | 76.0% | 83.3% | 86.1% |
| Nucleotides | 66.2% | 65.6% | 71.4% |
| Metals | 68.6% | 76.7% | 79.3% |
