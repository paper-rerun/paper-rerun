## Table 1 - split-appropriate reading of the ligand

| Split | n | Quantity | Paper | Ours | Diff |
|---|---|---|---|---|---|
| small_molecule | 316 | LigandMPNN | 63.3% | 60.9% | -2.4 |
| small_molecule | 316 | ProteinMPNN | 50.4% | 51.4% | +1.0 |
| nucleotide | 74 | LigandMPNN | 50.5% | 50.5% | -0.0 |
| nucleotide | 74 | ProteinMPNN | 34.0% | 31.5% | -2.5 |
| metal | 82 | LigandMPNN | 77.5% | 78.2% | +0.7 |
| metal | 82 | ProteinMPNN | 40.6% | 37.9% | -2.7 |

## Table 2 - full matrix, median recovery in percent

| Reading of 'near the ligand' | Model | small_molecule | nucleotide | metal |
|---|---|---|---|---|
| every non-protein atom (paper's literal wording) | ligand_mpnn | 57.8 (n=316) | 50.5 (n=74) | 59.7 (n=82) |
| every non-protein atom (paper's literal wording) | protein_mpnn_32 | 49.9 (n=316) | 31.5 (n=74) | 39.7 (n=82) |
| every non-protein atom (paper's literal wording) | protein_mpnn_48 | 47.2 (n=316) | 32.9 (n=74) | 40.6 (n=82) |
| metal atoms only | ligand_mpnn | 50.0 (n=49) | 66.2 (n=22) | 78.2 (n=82) |
| metal atoms only | protein_mpnn_32 | 41.4 (n=49) | 61.7 (n=22) | 37.9 (n=82) |
| metal atoms only | protein_mpnn_48 | - (n=None) | - (n=None) | - (n=None) |
| largest single het residue | ligand_mpnn | 60.9 (n=316) | 57.5 (n=49) | 60.2 (n=78) |
| largest single het residue | protein_mpnn_32 | 51.4 (n=316) | 30.0 (n=49) | 43.3 (n=78) |
| largest single het residue | protein_mpnn_48 | - (n=None) | - (n=None) | - (n=None) |

## LigandMPNN advantage over ProteinMPNN, percentage points

| Split | Paper | Ours |
|---|---|---|
| small_molecule | +12.9 | +9.5 |
| nucleotide | +16.5 | +18.9 |
| metal | +36.9 | +40.3 |

## Coverage

- small_molecule: 317 ids in the split, 316 scored, 0 with no run output, 1 with no residue meeting the cutoff, median 16 near-ligand residues per structure
- nucleotide: 74 ids in the split, 74 scored, 0 with no run output, 0 with no residue meeting the cutoff, median 26 near-ligand residues per structure
- metal: 83 ids in the split, 82 scored, 1 with no run output, 0 with no residue meeting the cutoff, median 10 near-ligand residues per structure
