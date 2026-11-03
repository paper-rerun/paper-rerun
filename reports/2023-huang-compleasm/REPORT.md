# Reproduction report: compleasm: a faster and more accurate reimplementation of BUSCO

- Paper: Huang, N., Li, H. "compleasm: a faster and more accurate reimplementation of BUSCO". Bioinformatics 39(10), btad595 (2023). DOI: 10.1093/bioinformatics/btad595 (PMC10558035, CC BY 4.0)
- Code: https://github.com/huangnengCSU/compleasm @ v0.2.2 = 8d33fa183483550c6113f84f8deace71807e9a74. We ran the release kit compleasm-0.2.2_x64-linux.tar.bz2 (671,502 B, md5 cefe5b8d17c3758add056af1cf4e40a5), which bundles miniprot 0.11-r234 and HMMER 3.3.2 hmmsearch. HEAD was not used for the graded runs.
- Data: the seven NCBI RefSeq assemblies listed in Table S1 (https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/...), and the BUSCO odb10 lineages from https://busco-data.ezlab.org/v5/data (now served from https://busco-data.s3.amazonaws.com). Only the 2024-01-08 re-release of each odb10 lineage is still available.
- Target: Table 1, compleasm rows. For each of the 7 reference genomes: Completed, Single-copy, Duplicated, Fragmented and Missing (%), plus N.
- Verdict: Not reproduced
- Date: 2026-11-03
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04 with 31 GB RAM. CPU only, 8 threads, nice 19. The RTX 2070 SUPER 8 GB was not used.

In six of the seven genomes, all 30 percentages fall within the pre-registered 0.3-point tolerance, but the agreement depends on that tolerance: none of the seven C values equals the paper at one decimal. In each of those six genomes C is 0.10 to 0.24 points higher and F 0.10 to 0.30 points lower than in the paper (*S. cerevisiae* F is 0 against the paper's 0.3, exactly at the tolerance edge). All seven N are exact. The human C, the abstract's 99.6%, is 99.84% here (99.8 at one decimal), within tolerance but not exact.

*Z. mays* does not match. We get C = 99.4% where the paper reports 96.7%, a difference of 2.7 points, and F = 0.3% where the paper reports 3.0%. The pre-registered rule says any C more than 1.0 point off means "Not reproduced", so that is the verdict.

We found no code cause for the maize gap: v0.2.2 and the current v0.2.10, which bundle different miniprot builds, give the same maize counts on the lineage that exists today. The one input we know changed is the lineage (the 2023 odb10 files are gone), but we could not test it directly, and a few inputs shared by both runs were not varied (listed under "Why maize differs").

## Results

Percentages are computed from the integer counts in each run's `summary.txt` (`runs/<tag>/summary.txt`). Scoring is done by `runs/score.py` and the output is in `runs/scores.tsv` and `runs/scores.json`. Definitions are pre-registered in `claims.json` (sha256 c57fc41e…7481, re-checked after the runs):

- C = (S + D) / N
- F = (Fragmented + Interspaced) / N. Interspaced was 0 in every run.
- M is taken as printed by the tool.
- Tolerance is 0.3 points. N must match exactly.

| Genome (lineage) | Quantity | Paper | Ours | Diff | Status |
|---|---|---|---|---|---|
| S. cerevisiae (saccharomycetes_odb10) | C | 99.2 | 99.44 | +0.24 | within 0.3 |
| | S | 97.6 | 97.85 | +0.25 | within 0.3 |
| | D | 1.6 | 1.59 | -0.01 | exact |
| | F | 0.3 | 0.00 | -0.30 | within 0.3 (at the edge) |
| | M | 0.5 | 0.56 | +0.06 | within 0.3 |
| | N | 2137 | 2137 | 0 | exact |
| C. elegans (nematoda_odb10) | C | 99.8 | 99.94 | +0.14 | within 0.3 |
| | S | 99.7 | 99.81 | +0.11 | within 0.3 |
| | D | 0.1 | 0.13 | +0.03 | exact |
| | F | 0.2 | 0.03 | -0.17 | within 0.3 |
| | M | 0.0 | 0.03 | +0.03 | exact |
| | N | 3131 | 3131 | 0 | exact |
| A. thaliana (brassicales_odb10) | C | 99.9 | 100.00 | +0.10 | within 0.3 |
| | S | 98.9 | 98.96 | +0.06 | within 0.3 |
| | D | 1.0 | 1.04 | +0.04 | exact |
| | F | 0.1 | 0.00 | -0.10 | within 0.3 |
| | M | 0.0 | 0.00 | 0.00 | exact |
| | N | 4596 | 4596 | 0 | exact |
| D. melanogaster (diptera_odb10) | C | 99.7 | 99.94 | +0.24 | within 0.3 |
| | S | 99.4 | 99.63 | +0.23 | within 0.3 |
| | D | 0.3 | 0.30 | +0.00 | exact |
| | F | 0.2 | 0.00 | -0.20 | within 0.3 |
| | M | 0.1 | 0.06 | -0.04 | exact |
| | N | 3285 | 3285 | 0 | exact |
| M. musculus (glires_odb10) | C | 99.7 | 99.89 | +0.19 | within 0.3 |
| | S | 97.8 | 97.96 | +0.16 | within 0.3 |
| | D | 1.9 | 1.93 | +0.03 | exact |
| | F | 0.3 | 0.06 | -0.24 | within 0.3 |
| | M | 0.0 | 0.05 | +0.05 | within 0.3 |
| | N | 13798 | 13798 | 0 | exact |
| H. sapiens T2T-CHM13 (primates_odb10) | C | 99.6 | 99.84 | +0.24 | within 0.3 |
| | S | 98.9 | 99.12 | +0.22 | within 0.3 |
| | D | 0.7 | 0.72 | +0.02 | exact |
| | F | 0.3 | 0.07 | -0.23 | within 0.3 |
| | M | 0.1 | 0.09 | -0.01 | exact |
| | N | 13780 | 13780 | 0 | exact |
| Z. mays (liliopsida_odb10) | C | 96.7 | 99.41 | **+2.71** | outside |
| | S | 82.2 | 83.99 | **+1.79** | outside |
| | D | 14.5 | 15.42 | +0.92 | close, outside tolerance |
| | F | 3.0 | 0.34 | **-2.66** | outside |
| | M | 0.3 | 0.25 | -0.05 | within 0.3 |
| | N | 3236 | 3236 | 0 | exact |

Our F is lower than the paper's in every genome. In the six small-offset genomes S and C rise by about the same amount as F falls; in *Z. mays* the 2.7-point gain in C splits into +1.8 S and +0.9 D. This is consistent with genes the paper counted as Fragmented being Complete here, but without the paper's per-gene tables we cannot confirm it. The shift is 0.1 to 0.3 points in six genomes and 2.7 points (about 86 of 3,236 genes) in maize.

Ungraded cross-check: Section 3.2 gives 13,622 complete single-copy genes on the whole CHM13; we get 13,659 (+37, 0.27 points).

Not run: the optional BUSCO rows of Table 1. Fig. 1a times, the Section 3.1 annotation checks and Tables S4-S7 were excluded in `claims.json`.

Variants we ran but did not grade:

| Run | S | D | F | I | M | N | Note |
|---|---|---|---|---|---|---|---|
| S. cerevisiae repeat (same input, -t 8) | 2091 | 34 | 0 | 0 | 12 | 2137 | miniprot GFF byte-identical; full_table.tsv has the same rows in a different order |
| --outs 0.97, S. cerevisiae | 2099 | 26 | 0 | 0 | 12 | 2137 | S 98.22% (paper 97.6, +0.62); D 1.22% (paper 1.6) |
| --outs 0.97, C. elegans | 3126 | 3 | 1 | 0 | 1 | 3131 | D 0.10% (paper 0.1; 0.13 at 0.95) |
| --outs 0.97, A. thaliana | 4568 | 28 | 0 | 0 | 0 | 4596 | S 99.39% (paper 98.9, +0.49); D 0.61% (paper 1.0) |
| --outs 0.97, D. melanogaster | 3274 | 9 | 0 | 0 | 2 | 3285 | |
| --outs 0.97, Z. mays | 2776 | 441 | 11 | 0 | 8 | 3236 | S 85.78% (paper 82.2, +3.58); D 13.63% (paper 14.5, -0.87); C 99.41 and F 0.34 unchanged from 0.95 |
| HEAD v0.2.10, --odb odb10, Z. mays | 2718 | 499 | 11 | 0 | 8 | 3236 | identical to v0.2.2; miniprot 0.12-r237 bundled with v0.2.10; library with the full 1,248-line index |
| HEAD v0.2.10, --odb odb10, S. cerevisiae | 2091 | 34 | 0 | 0 | 12 | 2137 | identical to v0.2.2; miniprot 0.12-r237 bundled with v0.2.10; library with the full 1,248-line index |

- **The 0.97 threshold.** Section 3.2 says miniprot ignores alignments below 97% of the best score. The 0.97 variant was run on the four small genomes and, during the revision of this report, on *Z. mays* (`runs/outs097_zmay`); it was not run on *M. musculus* or *H. sapiens*. On the four small genomes, `--outs 0.97` moves D away from the paper in *S. cerevisiae* and *A. thaliana* (and S outside tolerance: +0.62 and +0.49); in *C. elegans* D goes from 0.13 to 0.10, toward the paper's 0.1. On those four genomes the shipped default of 0.95 fits the paper better. In *Z. mays*, 0.97 leaves C and F exactly where they were (the same 11 Fragmented genes) and only moves 58 genes from D to S, which takes S further from the paper. So the threshold does not explain the maize gap.
- **Deviation from the pre-registration: v0.2.1 was planned if v0.2.2 missed, and was not run** because it would tell us nothing new. Its compleasm.py (md5 57ba4938…) differs from v0.2.2 in 208 changed lines, all in how the miniprot, hmmsearch and sepp executables are found (`search_miniprot`, `search_hmmsearch` and `search_sepp` move into a `CheckDependency` class) plus one comment, and it bundles the same miniprot (340998cb…) and hmmsearch (545731ff…) binaries. Evidence: `env/kit_v021_md5.txt` and `runs/v021_vs_v022.diff`.

## What it took

1. **Environment** (`env/setup.sh`, lock in `env/requirements.lock`).
   - We downloaded the v0.2.2 release kit and checked its size against the server, its md5, and its sha256.
   - We copied compleasm.py, miniprot (md5 340998cb…) and hmmsearch (md5 545731ff…) into `env/bin/` (md5s in `env/kit_md5.txt`).
   - We made a uv venv with Python 3.10.22, pandas 2.0.2 and numpy 1.24.3.
2. **Data** (`data/download.sh`).
   - Seven genomes (2.53 GB) and seven lineage tars (1.78 GB). Every file matched the server's Content-Length and the published md5: NCBI's `md5checksums.txt` for the genomes, `file_versions.tsv` for the tars. `file_versions.tsv` itself matched its `.hash` file (dadbe48e…). The logs are `data/download_check.tsv` and `data/download_verify.log` (final check, fail=0).
   - The lineages are extracted the same way v0.2.2's `download_lineage` does it. We also extracted `dataset.cfg`, and every one says `creation_date=2024-01-08` and `OrthoDB_version=10.1`.
   - The tool's own downloader was not used, because of issue #23.
   - The human and maize genomes were also fetched over a second connection to save time (`data/prefetch_big.sh`, `runs/helpers/kill_main_dl.sh`). For a short time two downloads wrote to the human file at once; this comes from our observation during the run, not from a log. The final md5 check passed for every file.
3. **Environment fix 1: the lineage index.** Unchanged, v0.2.2 crashes before doing any work with today's `file_versions.tsv`, because it splits each placement-file name on "." and expects three parts:
   ```
   File "compleasm.py", line 264, in download_placement
       prefix, version, sufix = strain.split(".")
   ValueError: too many values to unpack (expected 3)
   ```
   - The cause is new names like `list_of_reference_markers.eukaryota_odb12.2.txt` (log: `runs/fullindex_attempt/run.log`).
   - Our fix is in `data/prep_library.sh`. The `-L` library gets a copy of the index without the odb12 lines (214 of 1,248 lines are kept), which puts the index back in the naming the code was written for.
   - We also created empty `placement_files.done` and `eukaryota_odb10.done` markers, so that v0.2.2 does not download the placement files and eukaryota lineage. Those are only used by `--autolineage`, which we did not use.
   - No code was changed.
4. **Runs** (`runs/run_one.sh`, `runs/run_all.sh`). Each run was `compleasm.py run -a <genome>.fna.gz -o runs/<tag> -t 8 -l <lineage> -L data/mb_downloads --outs 0.95 --miniprot_execute_path env/bin/miniprot --hmmsearch_execute_path env/bin/hmmsearch` (0.95 is the default; all other options at defaults, mode busco). The full command is in each `runs/<tag>/time.txt`.
   - Genomes were used as downloaded from NCBI, in NCBI's contig order.
   - Wall times at 8 threads: S.cer 2:51, C.el 3:25, A.th 5:06, D.mel 6:24, M.mus 31:43, H.sap 23:32, Z.mays 13:46.
   - Peak RSS: mouse 23.4 GiB, maize 25.4 GiB, human 27.1 GiB (GNU time, KiB).
5. **Environment fix 2: the human run ran out of memory once.** The first attempt's miniprot was killed with SIGKILL (exit -9) during index building, at 20,639,044 KiB (19.7 GiB) max RSS per GNU time (`runs/hsap_attempt1_oom/run.log`, `time.txt`); we attribute it to the OOM killer, but the kernel log was not saved. The retry log is `runs/hsap_retry.log` (free -m before the retry: 31,048 MiB available).
   - We reran it unchanged and it finished.
6. **Total compute:** about 90 minutes for the primary runs, plus about 44 minutes for the variants (repeat, five `--outs 0.97` runs and two HEAD runs, summed from their `time.txt`). Downloads took about 70 minutes (file times 16:33 to 17:41), with the final verification done at 17:44.

## Why maize differs (diagnosis, not graded)

We found no code cause: compleasm v0.2.2 (miniprot 0.11-r234) and v0.2.10 (miniprot 0.12-r237) give identical maize counts.
- The HEAD run used its own library, `data/mb_downloads_head`, with the full 1,248-line index (binaries in `env/kit_head_md5.txt`, log in `runs/head_zmay/run.log`).
- Other than v0.2.2, the only release from before the paper was accepted is v0.2.1, and its alignment and scoring code is the same (see above).
- `--outs 0.97` does not change maize C or F either (see the variants).
- Not tested, and common to both runs: pandas 2.0.2 (same venv; `claims.json` D-ENV notes that an unstable `sort_values` could break ties differently), the same HMMER 3.3.2 hmmsearch binary (md5 545731ff…), and the maize genome as served today. The RefSeq record now carries the RS_2025_02 annotation (`data/genomes/GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0.md5checksums.txt`), and we do not have a 2023 md5 to compare the FASTA with.

The one input we know changed is the lineage.
- The 2023 odb10 tars are no longer served. In the 2024-01-08 re-release, `refseq_db.faa.gz` (the proteins miniprot aligns) is a new file, and `lengths_cutoff` (the per-gene Complete/Fragmented threshold) may be new as well. We checked this at triage.
- Maize's result is unusually sensitive to that threshold. 729 of its 3,217 complete genes (`runs/margin.py`) are within 5% of the threshold `length - 2*sigma`. Yeast has 5 and human has 6 in the same band. This sensitivity works in both directions.
- `liliopsida_odb10` also has 141 genes with sigma = 0 (305 with sigma <= 1; none in saccharomycetes or primates). The code turns sigma 0 into 1, which makes today's threshold stricter, so these genes do not by themselves explain why we see fewer Fragmented genes than the paper.
- For the paper to have about 86 more Fragmented maize genes than we do, the 2023 cutoffs would have to be stricter or the 2023 reference proteins would have to align shorter. Neither can be checked without the 2023 liliopsida_odb10 tar.
- The paper reports maize annotation completeness of 96.8% (Table S3) as agreeing with compleasm's 96.7%; our 99.4% exceeds it by 2.6 points. This counts against our number, not the paper's.

## Alternative readings

- **Folding Interspaced into F.** Interspaced was 0 in every run, so this choice changes nothing.
- **Using the tool's two-decimal output instead of the raw counts.** Rounding the tool's two-decimal print instead of the raw counts changes two one-decimal values: *S. cerevisiae* S (printed 97.85%) becomes 97.9 instead of 97.8, so the diff is +0.3, at the edge of the tolerance, and *Z. mays* M (printed 0.25%) becomes 0.3 instead of 0.2, matching the paper. Neither changes a status or the verdict.
- **Treating maize as a missing input rather than a non-reproduction.** If the lineage re-release is counted as a missing input, the six genomes that match would support "Partially reproduced". The pre-registered rule does not allow this, so it does not change the verdict.

## Notes for the authors

Hi! We re-ran Table 1 (compleasm rows) with the v0.2.2 release kit on the RefSeq assemblies from Table S1, using the 2024-01-08 odb10 lineages (the only ones still served). Six of the seven genomes agree within 0.3 points on every category, although in all six our C is 0.1 to 0.24 points higher and F lower (T2T-CHM13: 99.84% against 99.6%). *Z. mays* does not: we get 99.4 / 84.0 / 15.4 / 0.3 / 0.2 against the paper's 96.7 / 82.2 / 14.5 / 3.0 / 0.3. v0.2.10 with `--odb odb10` gives exactly the same maize counts, so it does not look like a code change. Our best guess is the lineage re-release: many maize genes sit close to the `length - 2*sigma` cutoff, so a change in liliopsida_odb10 could move them. If you still have the 2023 lineage tars, or the `full_table.tsv` from the paper runs, publishing them (for example on Zenodo) would settle it.

Two smaller things:
1. v0.2.2 crashes with `ValueError: too many values to unpack` in `download_placement` because today's `file_versions.tsv` contains odb12.2 names. That makes the published version hard to run as-is. A note in the README, or a tolerant parser, would help anyone reproducing the paper.
2. Section 3.2 says miniprot drops alignments below 97% of the best score, but the code default is `--outs 0.95`, and the help text says `[0.99]`. Stating which value was used in the paper would remove the ambiguity. On our runs of the four small genomes, 0.95 matches Table 1 better; on maize, 0.97 leaves C and F unchanged.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A separate agent read the paper and pre-registered the claims, definitions, tolerances and verdict rule in `claims.json` (hash frozen in `claims.sha256`) before any run. A single agent then built the environment, ran the authors' released code on a Ryzen 9 3900X (CPU only, 8 threads; the RTX 2070 SUPER was not used), compared the results with the paper and wrote this report. A reviewer agent and a reviser agent checked the report against the logs, and a human approved publication. This run did not include blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
