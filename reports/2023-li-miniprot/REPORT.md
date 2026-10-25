# Reproduction report: Protein-to-genome alignment with miniprot

- Paper: Li, H. "Protein-to-genome alignment with miniprot". Bioinformatics 39(1), btad014 (2023). DOI: 10.1093/bioinformatics/btad014 (PMID 36648328, preprint arXiv 2210.08052)
- Code: https://github.com/lh3/miniprot @ v0.7 = 2e57d1a735097f5a95ca71885181ffd7dae4c865 (r207), prebuilt miniprot-0.7_x64-linux.tar.bz2 from the release page. Evaluation: paftools.js from https://github.com/lh3/minimap2 @ 822ccd173358f11842b6dc54e17bbdcc2d9a0a9a (r1152), run with k8 1.2 (Zenodo 11357203)
- Data: Gencode v41 human (GRCh38.primary_assembly.genome.fa.gz, gencode.v41.annotation.gtf.gz), Gencode M30 mouse (gencode.vM30.pc_translations.fa.gz, gencode.vM30.annotation.gtf.gz), Ensembl 107 zebrafish (Danio_rerio.GRCz11.pep.all.fa.gz), Ensembl 107 fly (Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz, Drosophila_melanogaster.BDGP6.32.107.gtf.gz), Ensembl Metazoa 54 mosquito (Anopheles_gambiae.AgamP4.pep.all.fa.gz). The full URLs are in env/fetch.sh
- Target: Table 1, the four miniprot-0.7 columns: zebrafish->human -j2, zebrafish->human -j1, mouse->human -j2 and mosquito->fly -j2 -G 50k. That is 12 primary percentages (% confirmed junc., % base SN and % base SP for each column) and 20 count rows (16 checks with a tolerance, plus "# proteins", which is reported only)
- Verdict: **Partially reproduced** (6 of the 12 primary percentages are within 0.50 pp)
- Date: 2026-10-25
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04 with 31 GB RAM (WSL default limit, no .wslconfig), RTX 2070 SUPER 8 GB (not used; the run was CPU only)

## Results

Every Paper/Ours number in the claim tables comes from runs/results.json, which runs/scripts/compare.py wrote from the paftools output in runs/main/. The definitions and tolerances were frozen in claims.json before anything ran (sha256 af95fe40408e9fb954dd8a92558f2abd41b5c3230a0c065ab916d81c8dfa3fb9, frozen 2026-10-25T11:39:09-03:00). The review checked the same hash again after all runs and it had not changed (runs/logs/review2_recheck.log). Tolerances: 0.50 percentage points for percentages, 1% relative for counts, 10% relative for non-overlapping junctions. "# proteins" is reported only.

The verdict rule comes from claims.json. Reproduced means all 12 primary percentages are within 0.50 pp. Partially reproduced means some are. Not reproduced means none are. Count checks and test-set deviations are reported next to the verdict and don't change it.

### Primary percentages

| Column | Quantity | Paper | Ours | Diff (pp) | Within 0.50 pp |
|---|---|---|---|---|---|
| zebrafish->human, -j2 | % confirmed junc. | 92.16 | 92.16 | 0.00 | yes |
| zebrafish->human, -j2 | % base SN | 63.11 | 62.16 | -0.95 | no |
| zebrafish->human, -j2 | % base SP | 95.43 | 94.85 | -0.58 | no |
| zebrafish->human, -j1 | % confirmed junc. | 89.73 | 89.74 | +0.01 | yes |
| zebrafish->human, -j1 | % base SN | 63.16 | 62.21 | -0.95 | no |
| zebrafish->human, -j1 | % base SP | 94.91 | 94.33 | -0.58 | no |
| mouse->human, -j2 | % confirmed junc. | 97.15 | 97.10 | -0.05 | yes |
| mouse->human, -j2 | % base SN | 90.10 | 88.90 | -1.20 | no |
| mouse->human, -j2 | % base SP | 97.26 | 96.84 | -0.42 | yes |
| mosquito->fly, -j2 -G 50k | % confirmed junc. | 87.44 | 87.44 | 0.00 | yes |
| mosquito->fly, -j2 -G 50k | % base SN | 56.10 | 56.10 | 0.00 | yes |
| mosquito->fly, -j2 -G 50k | % base SP | 96.69 | 95.85 | -0.84 | no |

All four junction percentages reproduce. The base SN and SP rows are where it breaks: 6 of the 8 base percentages are outside the tolerance, all of them low, by 0.58 to 1.20 pp. Of the other two, mosquito base SN matches exactly and mouse base SP is 0.42 pp low. The paper says least about the reference used for base SN/SP ("longest transcripts"). See Alternative readings.

### Count checks

| Column | Quantity | Paper | Ours | Diff | Rel. diff | Within tolerance |
|---|---|---|---|---|---|---|
| zebrafish->human, -j2 | # proteins | 25,007 | 25,094 | +87 | +0.35% | reported only |
| zebrafish->human, -j2 | # multi-exon | 16,866 | 16,929 | +63 | +0.37% | yes (1%) |
| zebrafish->human, -j2 | # predicted junc. | 157,918 | 158,226 | +308 | +0.20% | yes (1%) |
| zebrafish->human, -j2 | # non-ovlp. junc. | 482 | 496 | +14 | +2.90% | yes (10%) |
| zebrafish->human, -j2 | # confirmed junc. | 145,545 | 145,824 | +279 | +0.19% | yes (1%) |
| zebrafish->human, -j1 | # proteins | 25,007 | 25,094 | +87 | +0.35% | reported only |
| zebrafish->human, -j1 | # multi-exon | 17,104 | 17,153 | +49 | +0.29% | yes (1%) |
| zebrafish->human, -j1 | # predicted junc. | 161,295 | 161,597 | +302 | +0.19% | yes (1%) |
| zebrafish->human, -j1 | # non-ovlp. junc. | 802 | 815 | +13 | +1.62% | yes (10%) |
| zebrafish->human, -j1 | # confirmed junc. | 144,734 | 145,013 | +279 | +0.19% | yes (1%) |
| mouse->human, -j2 | # proteins | 21,844 | 22,335 | +491 | +2.25% | reported only |
| mouse->human, -j2 | # multi-exon | 17,065 | 17,322 | +257 | +1.51% | no (1%) |
| mouse->human, -j2 | # predicted junc. | 167,446 | 167,748 | +302 | +0.18% | yes (1%) |
| mouse->human, -j2 | # non-ovlp. junc. | 330 | 360 | +30 | +9.09% | yes (10%) |
| mouse->human, -j2 | # confirmed junc. | 162,675 | 162,879 | +204 | +0.13% | yes (1%) |
| mosquito->fly, -j2 -G 50k | # proteins | 13,094 | 13,094 | 0 | 0.00% | reported only |
| mosquito->fly, -j2 -G 50k | # multi-exon | 6,675 | 6,676 | +1 | +0.01% | yes (1%) |
| mosquito->fly, -j2 -G 50k | # predicted junc. | 22,614 | 22,615 | +1 | +0.00% | yes (1%) |
| mosquito->fly, -j2 -G 50k | # non-ovlp. junc. | 488 | 488 | 0 | 0.00% | yes (10%) |
| mosquito->fly, -j2 -G 50k | # confirmed junc. | 19,774 | 19,774 | 0 | 0.00% | yes (1%) |

15 of the 16 count checks are within tolerance. The one miss is mouse "# multi-exon" (+1.51%).

### Test-set deviation

The paper doesn't publish an id list, only the rule "longest protein for each gene". Before running, we fixed one rule per species (claims.json, D-TESTSET-*):

- Mosquito, longest protein per gene over all of pep.all: 13,094, the same as the paper.
- Zebrafish, protein_coding genes on chromosomes 1-25: 25,094, which is 87 (0.35%) more than the paper.
- Mouse, Ensembl canonical translations from Gencode M30, which is how the README at tag v0.7 describes the mouse set: 22,335, which is 491 (2.25%) more than the paper. This is the bigger of the two deviations, and most likely why the mouse "# multi-exon" check is off by 1.51%: with either 21,844-protein variant below, that count comes out at 17,065 or 17,070. Two of the pre-registered variants give exactly 21,844 (see Alternative readings). Neither was the main rule, so the table above keeps the canonical set.

Only the mosquito test set matches exactly, and that column matches the paper within 1 on every count. It also matches exactly on % confirmed junc. and % base SN. Its base SP is still 0.84 pp low, so at least in this column the test set is not what causes the base SP gap.

### Elapsed time and peak RAM (not checked)

We **did not check** the time and RAM rows of Table 1 as claims. They depend on the machine, and the paper doesn't give the thread count. The values below are for the record only. They come from miniprot's own log line and from /usr/bin/time -v (runs/main/*.miniprot.log and *.time), with -t16. miniprot prints peak RSS in GiB (bytes / 1024^3) and labels it GB. We assume the paper's values came from the same log line.

| Column | Paper time (s) | Ours (s) | Paper peak RAM (GB) | Ours (GB) |
|---|---|---|---|---|
| zebrafish->human, -j2 | 267 | 326.3 | 21.8 | 28.45 |
| zebrafish->human, -j1 | 257 | 334.3 | 22.5 | 28.45 |
| mouse->human, -j2 | 164 | 238.8 | 15.3 | 28.45 |
| mosquito->fly, -j2 -G 50k | 34 | 36.8 | 3.9 | 4.45 |

We checked memory before indexing (runs/logs/memory.log, also appended to runs/logs/setup.log). There is no .wslconfig, so WSL used its default limit: MemTotal 32,818,700 kB (31 GB), MemAvailable 31,348,844 kB, swap 8 GB. The GRCh38 runs peaked at 28.45 GB. That is 6.0 to 6.7 GB above the paper's zebrafish columns, 13.1 GB above its mouse column, and about 3 GB below our limit. At the memory check before indexing, 1 GB was in use and 29 GB were free. Anyone repeating this on a 32 GB machine should run nothing else at the same time.

## Alternative readings

These readings were listed in claims.json before the main run, and we computed them only after the main result was final (runs/scripts/run_alt.sh, outputs in runs/alt/, tabulated in runs/results.json under "alt"). They are not used for the verdict.

### Evaluation options (same alignments as the main run)

| Reading | zf -j2 conf / SN / SP | zf -j1 conf / SN / SP | mouse conf / SN / SP | mosquito conf / SN / SP |
|---|---|---|---|---|
| Paper | 92.16 / 63.11 / 95.43 | 89.73 / 63.16 / 94.91 | 97.15 / 90.10 / 97.26 | 87.44 / 56.10 / 96.69 |
| Main (-1, longest-CDS reference) | 92.16 / 62.16 / 94.85 | 89.74 / 62.21 / 94.33 | 97.10 / 88.90 / 96.84 | 87.44 / 56.10 / 95.85 |
| ALT-1: no -1 | 92.01 / 63.21 / 94.47 | 89.62 / 63.19 / 93.94 | 96.85 / 89.74 / 96.56 | 87.31 / 56.69 / 95.80 |
| ALT-2: -1 -c | 92.17 / 62.16 / 94.84 | 89.75 / 62.22 / 94.32 | 97.11 / 88.89 / 96.84 | n/a |
| ALT-1x2: -c, no -1 | 92.04 / 63.21 / 94.47 | 89.64 / 63.19 / 93.94 | 96.86 / 89.72 / 96.56 | n/a |
| ALT-3: junceval -l 1 | 92.16 / - / - | 89.74 / - / - | 97.10 / - / - | 87.44 / - / - |
| ALT-3: junceval -l 3 | 92.36 / - / - | 89.98 / - / - | 97.24 / - / - | 87.58 / - / - |
| ALT-4: all CDS as reference | - / 59.60 / 95.44 | - / 59.65 / 94.92 | - / 85.08 / 97.26 | - / 55.42 / 96.69 |
| ALT-5: longest spliced transcript | - / 62.23 / 89.75 | - / 62.29 / 89.28 | - / 89.03 / 91.66 | - / 56.43 / 94.53 |
| ALT-6: longest CDS, protein_coding genes | - / 62.34 / 94.82 | - / 62.39 / 94.29 | - / 89.09 / 96.74 | - / 56.10 / 95.85 |
| ALT-7: primary_assembly GTF | 92.17 / 62.12 / 94.85 | 89.74 / 62.18 / 94.33 | 97.11 / 88.86 / 96.84 | n/a |
| ALT-7: basic GTF | 91.92 / 62.21 / 94.88 | 89.50 / 62.27 / 94.36 | 96.84 / 88.97 / 96.86 | n/a |

Two things stand out. Both are observations made after the main run and don't change the verdict.

- When all CDS lines are the reference (ALT-4), base SP matches the paper in all four columns: 95.44 vs 95.43, 94.92 vs 94.91, 97.26 vs 97.26 and 96.69 vs 96.69. The table legend defines SP as bases "covered by annotated coding regions". The SN definition says "longest transcripts", but the SP definition doesn't. That suggests the paper computed SP against all CDS. The same ALT-4 run, however, drops base SN to 55-85%, so if this is what happened, SN and SP were computed against different references, for example in two exoneval calls.
- Under the main reading the three human base SN values are 0.95 to 1.20 pp low. The only pre-registered reading that brings them within 0.50 pp is ALT-1 (no -1): 63.21, 63.19 and 89.74, against 63.11, 63.16 and 90.10. The same change moves mosquito SN from an exact 56.10 to 56.69, lowers SP in all four columns, and lowers % confirmed junc. by 0.12 to 0.25 pp. So no single pre-registered reading matches all base values. The script used to build the paper's longest-transcript reference is not published, and we didn't try readings outside the pre-registered list.

### Test-set variants (new alignments, main evaluation)

| Variant | # proteins | -j2 conf / SN / SP | -j1 conf / SN / SP |
|---|---|---|---|
| Paper, zebrafish | 25,007 | 92.16 / 63.11 / 95.43 | 89.73 / 63.16 / 94.91 |
| Main TS-ZF (protein_coding, chr 1-25) | 25,094 | 92.16 / 62.16 / 94.85 | 89.74 / 62.21 / 94.33 |
| ALT-ZF-A: all of pep.all | 30,313 | 92.12 / 62.53 / 94.56 | 89.72 / 62.62 / 93.98 |
| ALT-ZF-B: plus MT | 25,107 | 92.16 / 62.17 / 94.83 | 89.74 / 62.23 / 94.31 |
| ALT-ZF-B: all regions, no CHR_ALT | 25,432 | 92.13 / 62.40 / 94.77 | 89.69 / 62.46 / 94.24 |
| ALT-ZF-C: protein_coding transcript | 25,081 | 92.16 / 62.16 / 94.85 | 89.74 / 62.21 / 94.33 |

| Variant | # proteins | # multi-exon | conf / SN / SP |
|---|---|---|---|
| Paper, mouse | 21,844 | 17,065 | 97.15 / 90.10 / 97.26 |
| Main TS-MM (Ensembl canonical, no filter) | 22,335 | 17,322 | 97.10 / 88.90 / 96.84 |
| ALT-MM-A: longest per protein_coding gene with CDS | 21,844 | 17,065 | 97.13 / 88.80 / 96.85 |
| ALT-MM-B: canonical, protein_coding genes only | 21,844 | 17,070 | 97.14 / 88.81 / 96.86 |

ALT-MM-A gives exactly the paper's protein count and "# multi-exon". claims.json quotes 21,919 from triage for this rule, while the scripted count in runs/logs/testsets.log is 21,844. The review traced the difference: triage counted protein_coding genes with CDS in the M30 GTF (21,919), and 75 of those genes have no record in gencode.vM30.pc_translations.fa.gz, so the protein set has 21,844 (runs/logs/review2_recheck.log). Across all test sets the percentages move by 0.41 pp at most (zebrafish ALT-ZF-A, -j1 SN), and the mouse base SN stays 1.2-1.3 pp low. So the choice of test set doesn't explain the base SN gap.

### Other checks

- ALT-T: running the mosquito column with -t4 gives a PAF that is byte-identical to the -t16 run (runs/alt/ALT-T.txt).
- ALT-BIN (building from source) wasn't needed. The prebuilt binary ran and reports 0.7-r207.

## What it took

1. Download (env/fetch.sh) and verification (env/setup.sh). fetch.sh only compares each file with the server's Content-Length. setup.sh calls fetch.sh first and then checks the checksums. The first download attempt died silently: it left GRCh38.primary_assembly.genome.fa.gz at 93,711,360 bytes and wrote nothing to the log. We changed fetch.sh to send curl's stderr to runs/logs/fetch.log. We also corrected its header comment, which wrongly said it checked published checksums. Then we ran setup.sh again from 11:45:40. curl resumed the partial file, and every file reached the server size (runs/logs/fetch.log, "downloads done").
2. runs/logs/setup.log shows md5 OK for the 6 Gencode files against MD5SUMS and BSD sum OK for the 4 Ensembl files against CHECKSUMS. It also shows md5 OK for k8-1.2.tar.bz2 (Zenodo) and sha256 OK for paftools.js at r1152. The printed versions are miniprot 0.7-r207, k8 1.2-r137 and paftools 2.24-r1152-dirty. setup.sh then wrote env/lock.sha256. The review ran `sha256sum -c env/lock.sha256` after all runs, and all 13 files were OK (runs/logs/review2_recheck.log).
3. Test sets (runs/scripts/testsets.py) and the longest-CDS reference GTFs (runs/scripts/reduce_gtf.py: 20,427 human genes, 13,968 fly genes). The counts are in runs/logs/testsets.log and runs/logs/main.log.
4. Main run (runs/scripts/run_main.sh, log runs/logs/main.log), from 12:23 to 12:40: about 17 minutes for all four columns, indexing included. We added a memory check before indexing to this script. The commands are the pre-registered ones:
   - `miniprot -t16 -j2 GRCh38.primary_assembly.genome.fa.gz zebrafish.longest.faa`, then the same with `-j1`, mouse with `-j2`, and mosquito with `-t16 -j2 -G 50k` on the BDGP6.32 toplevel FASTA. All FASTA files were used as distributed, with contig order unchanged (miniprot issue #79).
   - `k8 paftools.js junceval -a -1 <full annotation GTF> <paf>`
   - `k8 paftools.js exoneval -a -s -1 <longest-CDS GTF> <paf>`
5. Comparison (runs/scripts/compare.py -> runs/results.json, runs/logs/compare.log).
6. Alternative readings (runs/scripts/run_alt.sh, log runs/logs/alt.log), from 12:40 to 13:41, started after compare.py had written the main result at 12:40:22 (runs/logs/compare_main.log). Most of that hour went to the 10 extra GRCh38 alignments.

We changed nothing in miniprot, paftools.js or any other author code, so there is no patches/ folder. The only edits were to our own scripts: stderr logging and the comment fix in fetch.sh, and the memory check in run_main.sh. We used no GPU.

## Notes for the authors

Draft issue for lh3/miniprot. Nothing has been posted.

> Hello! Thanks for releasing the binaries and the evaluation code, they made this easy to re-run. We re-ran the four miniprot-0.7 columns of Table 1 in the Bioinformatics paper. We used the v0.7 release binary, Gencode v41 / M30, Ensembl 107 / Metazoa 54 and paftools.js r1152. The junctions reproduce well: % confirmed junc. is within 0.05 pp in all four columns, and the mosquito->fly column matches within 1 on every count. Base SN and SP are the part we could not match exactly:
>
> 1. Base SP matches all four columns (95.44, 94.92, 97.26, 96.69) when exoneval uses all CDS lines of the GTF as the reference. Base SN does not match with that reference. With a longest-CDS-per-gene reference, the human SN values are 0.95-1.2 pp below the paper (62.16, 62.21, 88.90 vs 63.11, 63.16, 90.10), while fly SN matches exactly (56.10). Without -1, the human SN values come within 0.4 pp (63.21, 63.19, 89.74), but fly SN moves to 56.69 and SP drops in all four columns. Could you share how the "longest transcripts" GTF was made? The exact exoneval and junceval command lines would also help, in particular whether -1 was used.
> 2. The test sets: is the list of query protein ids available? For mouse, the paper says longest protein per gene, and the v0.7 README says Ensembl canonical. Taking the longest translation per protein_coding gene in M30 gives exactly 21,844, and so does canonical restricted to protein_coding genes. Canonical without that filter gives 22,335. For zebrafish, the closest rule we found (protein_coding, chromosomes 1-25) gives 25,094 vs 25,007.
> 3. Minor: with -t16 on GRCh38, peak RSS on our machine was 28.45 GB as printed by miniprot, against 21.8-22.5 GB for the zebrafish columns and 15.3 GB for mouse in the table. That may matter for people with 32 GB of RAM.
>
> This check was run by AI agents on a home computer and reviewed by a human before posting. Full report, with every command and log: https://github.com/paper-rerun/paper-rerun/blob/main/reports/2023-li-miniprot/REPORT.md. How we work: https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

One agent triaged the paper and checked that the code, data and checksums were public. A second agent read the paper and listed the numeric claims to check. Before anything ran, it fixed from the paper text every definition the computation needs: the test-set rules, the evaluation options, the tolerances and the alternative readings. That list is claims.json, frozen with a sha256 at 11:39 on 2026-10-25. A reviewing agent checked its 32 paper values against Table 1 in tex/miniprot.tex. The agent assigned to the runs then stopped early and returned a status note instead of a report, while the data download had in fact died, so the first error-hunting review only had that note to check (review.json). A third agent finished the work: it built the environment, ran the authors' released binary and evaluator on a Ryzen 9 3900X, CPU only, compared the results with the paper and wrote this report. A separate agent that took no part in the runs then checked the report against claims.json, Table 1 and the logs and outputs, re-ran some of the evaluations, and corrected the text (review2.json). For this paper, no agent recomputed the claims blind with scoring code of its own. A human reads the report before anything is published.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues