# Reproduction report: Multiple protein structure alignment at scale with FoldMason

- Paper: Gilchrist, C. L. M., Mirdita, M., Steinegger, M., Science 391(6784):485-488, 2026. DOI: 10.1126/science.ads6733 (the bioRxiv preprint 10.1101/2024.08.01.606130 is a different, earlier analysis and was not used)
- Code: https://github.com/steineggerlab/foldmason @ dd3c23500ce0893bc1b5f9b4a3e17c63796a5d0b (release 4-dd3c235, Zenodo 10.5281/zenodo.17315302), run from the bioconda build `foldmason-4.dd3c235-h5021889_0` (md5 e902225dd97295d28e8fb30bd1ad034e); analysis scripts https://github.com/steineggerlab/foldmason-analysis @ d356c402458123499fa39596b9be797d95d5f593
- Data: Zenodo 10.5281/zenodo.17311030 (foldmason_data.tar.gz). AlphaFold DB model_v6 PDBs were downloaded on 2026-10-27 and saved as AF-<acc>-F1-model_v4.pdb, because v4 returns 404 and the file name affects the alignment (issue #35). 2,915 of the 3,200 benchmark members are available. HOMSTRAD release homstrad_with_PDB_2024_Dec_1 could not be obtained (server offline).
- Target: Fig. 2A (HOMSTRAD full and hard, sum-of-pairs, FoldMason and FoldMason Fast) and Fig. 2B (AFDB clusters, full-MSA LDDT, overall and per domain count). Claims C1-C6 and S1-S10 are pre-registered in claims.json (sha256 4d903d3d32da38ab1d0ef3384ca62a3c8590be910d924d0e848a4e83f5dc3714).
- Verdict: Partially reproduced. AFDB: 31 of the 32 clusters whose inputs are still complete give the authors' per-cluster LDDT to 6 decimals in both modes; the 160-cluster means (C5, C6, S6-S10) could only be run on reduced inputs, because 285 structures were deleted from AFDB. HOMSTRAD (C1-C4, S1-S5): could not run, reference data unavailable.
- Date: 2026-10-27
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04.1 (31 GB RAM visible to WSL), RTX 2070 SUPER 8 GB (not used). Light mode: CPU only, nice 19, at most 4 processes.

## Summary

FoldMason does what the paper says on the AFDB benchmark, as far as the surviving inputs allow us to check.

1. **AFDB, complete clusters: exact.** 32 of the 160 benchmark clusters still have all 20 members, with the same sequences as the authors' MSAs. On 31 of them our LDDT equals the authors' published value to 6 decimals, in default and Fast mode, and our MSA file is identical to theirs. The 32nd cluster (A0A7X9A1N2) differs by -0.0008 (default) and -0.0089 (Fast). Its alignment differs too, and the authors' own MSA scored on our structures gives 0.541678 instead of their 0.542104. The alignment is not the only thing that moved, then: at least one v6 structure in this cluster has coordinates that differ from the v4 file the authors used. FoldMason gave the same MSA in two more reruns of this cluster, so this is not run-to-run noise.
2. **AFDB, 160-cluster means: reduced inputs only.** 285 of the 3,200 members (8.9%) were deleted from UniProt and have no AFDB model in any version, so 128 clusters run with 13 to 19 members instead of 20. Our means over the 160 clusters are 0.0023 to 0.0095 above the paper values. All of these gaps fall inside the pre-registered tolerances (1 SEM). They are not the pre-registered quantity, though, so they count as a reduced run and give no match verdict. On the 128 reduced clusters our LDDT is higher than the authors' in 84 (default) and 91 (Fast). That fits a smaller cluster being easier to align, not a change in the tool.
3. **HOMSTRAD: could not run.** The HOMSTRAD server still refuses connections on port 443 (checked again on 2026-10-27, `runs/homstrad_probe_2.log`). The Wayback Machine has no capture of the release tarball, and the Zenodo deposit 17311030 has no HOMSTRAD reference alignments or member PDBs (0 matching paths in its 33,361-entry listing). Without the reference there is no sum-of-pairs score.

How we got here: the first attempt could not run FoldMason at all. This machine's permission system refused to execute the release binary downloaded from GitHub, twice (`runs/blocked_actions.log`), and we did not try to get around it. For this rerun we installed the same release, 4-dd3c235, from bioconda in a micromamba environment inside `env/bioconda/`. The package md5 matches anaconda.org, and `foldmason version` prints `4.dd3c235`. Bioconda compiles from source, so this is not byte-for-byte the GitHub binary. Exact LDDT on 31 of 32 complete clusters shows it computes the same thing here.

## Results

| Quantity | Paper (from authors' TSV) | Ours | Diff | Status |
|---|---|---|---|---|
| C1 HOMSTRAD full, FoldMason, mean sp_fwd | 90.014 | not run | n/a | could not run (no HOMSTRAD reference) |
| C2 HOMSTRAD full, FoldMason, mean sp_rev | 89.732 | not run | n/a | could not run |
| C3 HOMSTRAD hard (55), FoldMason, mean sp_fwd | 77.149 | not run | n/a | could not run |
| C4 HOMSTRAD hard (55), FoldMason, mean sp_rev | 77.147 | not run | n/a | could not run |
| C5 AFDB 160 clusters, FoldMason, mean LDDT | 0.6050 | 0.6119 | +0.0069 (tol. 0.0102) | reduced inputs, no verdict |
| C6 AFDB 160 clusters, FoldMason Fast, mean LDDT | 0.6071 | 0.6134 | +0.0063 (tol. 0.0105) | reduced inputs, no verdict |
| S1 HOMSTRAD full, FoldMason F1 | 89.873 | not run | n/a | could not run |
| S2-S5 HOMSTRAD, FoldMason Fast (full fwd/rev, hard fwd/rev) | 89.271 / 89.188 / 72.322 / 72.671 | not run | n/a | could not run |
| S6-S9 AFDB, FoldMason, per domain count (1/2/3/4) | 0.7241 / 0.5638 / 0.5604 / 0.5717 | 0.7279 / 0.5713 / 0.5680 / 0.5805 | +0.0038 / +0.0075 / +0.0076 / +0.0088 | reduced inputs, no verdict |
| S10 AFDB, FoldMason Fast, per domain count (1/2/3/4) | 0.7280 / 0.5720 / 0.5610 / 0.5672 | 0.7344 / 0.5743 / 0.5683 / 0.5767 | +0.0064 / +0.0023 / +0.0073 / +0.0095 | reduced inputs, no verdict |

The check that uses the authors' exact inputs (`runs/afdb/compare_run.log`, `per_cluster_diff.tsv`):

| 32 complete clusters (7/7/10/8 by domain count) | Authors | Ours | Clusters equal to 1e-6 | Max abs. diff |
|---|---|---|---|---|
| FoldMason, mean LDDT | 0.6219 | 0.6219 | 31 / 32 | 0.0008 (A0A7X9A1N2) |
| FoldMason Fast, mean LDDT | 0.6285 | 0.6282 | 31 / 32 | 0.0089 (A0A7X9A1N2) |

On the 128 reduced clusters, the mean difference to the authors' per-cluster value is +0.0087 (default) and +0.0080 (Fast), with a largest absolute difference of 0.070 and 0.091. These clusters have 1 to 7 members fewer than the authors', so the per-cluster numbers are listed but not compared. No cluster gave NaN (320 of 320 LDDT values are finite).

We could not read the paper text, Fig. 2 or Tables S1/S2 from this machine. science.org returns HTTP 403 behind a Cloudflare check, and we did not bypass it. The "Paper" column therefore holds the means of the authors' released per-family scores (`data/homstrad_scores.tsv` md5 598b22949f7c37ba1964feee7400fcb1, `data/afdb_scores.tsv` md5 1a099615a11bcfe80bdcc67355a85a04), aggregated with the logic of their `FoldMason_benchmarks.R`. Someone with Science access still needs to check these values against the printed figure.

Input checks:

| Check | Result |
|---|---|
| Zenodo foldmason_data.tar.gz size / md5 | 4,511,287,230 B / 543c92bd16ab2bbdd2ab1125fcb01f91, both match the record (`runs/dl_zenodo.log`) |
| GitHub `data/*.tsv` vs Zenodo `results/*.tsv` (`runs/zenodo_inspect/check_results_tsv.log`) | byte-identical: afdb_scores.tsv 1a099615a11bcfe80bdcc67355a85a04, homstrad_scores.tsv 598b22949f7c37ba1964feee7400fcb1, afdb_families.tsv 6d62a487d51d463da6b28f1025e71a69, homstrad_families.tsv a4d51503e01fe879c2d1e378cc08ea5b |
| FoldMason bioconda package (`env/bioconda/setup.log`) | foldmason-4.dd3c235-h5021889_0.conda, md5 e902225dd97295d28e8fb30bd1ad034e, matches anaconda.org; binary sha256 318a74841855548dee59cfee34479322fd318599ed12ff00a1ba42f0c7d3b9ab; `foldmason version` = 4.dd3c235 |
| HOMSTRAD server and Wayback capture (`runs/homstrad_probe.log`, `runs/homstrad_probe_2.log`) | server: connection timeout on port 443 (three times, latest 2026-10-27T17:33Z); Wayback CDX: HTTP 200, no captures |
| HOMSTRAD reference MSAs or member PDBs in Zenodo 17311030 (`runs/zenodo_record_check.log`) | none; the record has one file, and its listing has no `*_msa.fasta`, `homstrad/*/pdbs/` or HOMSTRAD tarball |
| AFDB members downloaded (v6, saved under v4 name), each checked against stored gzip size and server md5 | 2,915 of 3,200; second try on 2026-10-27T17:27Z got 404 for the same 285 (`runs/afdb_download/refetch.log`); all 2,915 files on disk match their recorded size |
| AFDB members with no model: v6 404, prediction API HTTP 404, v1-v5 404 (`probe_versions.tsv`) | 285 |
| UniProt status of those 285 (`missing_status.tsv`) | all deleted: 152 "not part of a reference proteome", 87 "excluded proteome", 26 deleted from EMBL, 10 from RefSeq, 3 from Ensembl, 7 redundant |
| Clusters with all 20 members still available | 32 of 160 (7, 7, 10 and 8 for 1, 2, 3 and 4 domains) |
| v6 sequence equal to the ungapped v4 sequence in the authors' published foldmason_aa.fa | 2,915 / 2,915 |
| v4 copies of benchmark members inside afdb_scaling/pdbs.tar.gz (100,000 structures) | 0, so coordinate changes from v4 to v6 could not be checked directly |

## What it took

The first session took about 1.5 hours (10:39 to 12:15 local time), almost all of it spent waiting on downloads. The revision added about 25 minutes of network probes. The rerun took about 30 minutes, and the FoldMason run itself took 6 minutes on 4 processes (first output 14:34:39, last 14:40:30 local time). Summed wall time per call was 583 s for default mode and 508 s for Fast mode over 160 clusters, or 3.6 s and 3.2 s per cluster, single thread.

1. **First environment, blocked** (`env/setup.sh`, `env/lock.txt`). We downloaded the 4-dd3c235 `foldmason-linux-avx2.tar.gz` from the GitHub release and checked its size. The local permission system refused to execute it in the first session and again in the revision (`runs/blocked_actions.log`; only the second refusal has the exact command on record). That binary was never run, and we did not try to get around the refusals. We did not install t-coffee, because only HOMSTRAD needs it.
2. **Rerun environment** (`env/bioconda/setup.sh`, `setup.log`, `foldmason.explicit.txt`). micromamba 2.0.5-0, copied from another project folder on this machine and checked against its release sha256, created an env from conda-forge and bioconda with strict channel priority. `bioconda::foldmason=4.dd3c235=h5021889_0` is the only bioconda build of this release for linux-64. The exact package list with md5s is in `foldmason.explicit.txt`. Nothing was refused in this session.
3. **Zenodo data** (`env/dl_zenodo.sh`, `runs/dl_zenodo.log`). aria2c took 31 minutes, at an average of 2.3 MiB/s. Size and md5 match. We listed the archive (`runs/zenodo_inspect/tar_listing.txt`) and extracted only `info.txt`, the authors' `afdb_clusters/*/foldmason_aa.fa` and `foldmason_fast_aa.fa`, and the four `results/*.tsv` tables. The Zenodo API shows one older version of the deposit (record 15131366, April 2025, 4,400,048,397 B). We did not download it.
4. **HOMSTRAD** (`runs/homstrad_probe.sh`, `.log`, `homstrad_probe_2.log`). The server timed out on port 443 and the Wayback CDX index has no capture of the release tarball. Issue #38 says someone found a link but does not give it.
5. **AFDB structures** (`runs/afdb_download/`).
   - The first attempt used aria2c with 4 parallel requests and hit HTTP 429. That attempt left no log; the only record is a comment in `download_afdb.sh` and `fetch_afdb.py`.
   - The stdlib downloader `fetch_afdb.py` fetches one file at a time. The server sends PDBs as chunked gzip with no plain Content-Length, so each file is checked against `x-goog-stored-content-length` and the `x-goog-hash` md5 of the gzip object before decompression (`sizes.tsv`).
   - `check_missing.py` and `probe_versions.py` record why the 285 are missing (see the input checks). `refetch.sh` tried all 285 again during the rerun and got 404 for every one.
6. **v4 vs v6** (`runs/v4_vs_v6/`). None of the benchmark members are in `afdb_scaling/pdbs.tar.gz`, so the v4 coordinates are not available. All downloaded v6 sequences match the authors' MSAs.
7. **FoldMason runs** (`runs/afdb/`).
   - `run_cluster.sh` repeats the FoldMason commands of the authors' `align_family.sh`: `easy-msa <pdbs> out tmp --threads 1`, the same with `--fast`, and `msa2lddtreport` on both MSAs against the default run's structure DB, without `--only-scoring-cols`. The only edit for the rerun is the binary path.
   - `run_all.sh` runs 4 clusters at a time under nice 19 and collects LDDT with the authors' `extractLDDT.awk` (`our_afdb_scores.tsv`, 640 rows: LDDT and column counts for 160 clusters times 2 modes). The end timestamp in `run_all.log` is wrong (the shell printed it at start); the file times above are the real ones.
   - `compare.py` (`compare_run.sh`, `compare_run.log`) reports the 32 complete clusters against the authors' values, lists the 128 reduced ones, and labels every 160-cluster mean as reduced-input. A self-test with the authors' scores as ours gives 32/32 exact (`compare_selftest.log`).
   - `check_A0A7X9A1N2.sh` and `.log` cover the one complete cluster that does not match: two reruns from scratch, both giving the same MSA md5 as the main run, and the authors' published MSAs scored on our structures.

We made no changes to the authors' code, and `patches/` is empty.

## Notes for the authors

Thanks for publishing per-family scores and every tool's MSA. With them we could check FoldMason cluster by cluster, and 31 of 32 AFDB clusters with intact inputs match exactly. Two inputs are going away:

- **HOMSTRAD.** The server has been down since about May 2026 (issue #38), the Wayback Machine has no copy of `homstrad_with_PDB_2024_Dec_1.tar.gz`, and the Zenodo deposit has no reference alignments or member PDBs. Depositing that tarball, or the output of `clean_homstrad.py`, would make Fig. 2A reproducible again.
- **AFDB.** 285 of the 3,200 benchmark members (8.9%) are deleted and have no model in any AFDB version, which leaves 32 of 160 clusters complete. In cluster A0A7X9A1N2 the v6 coordinates also differ from what you scored. The v4 PDBs you used would be about 190 MB gzipped and would fix both problems.
- Small script issues: `compute_scores.sh` calls `compute_nirmsd`, which is not defined, and `FoldMason_benchmarks.R` filters `tool != "Homstrad"` while `name_map` produces `"HOMSTRAD"`.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder. The few statements that have no log (two refusals in the first session, the first aria2c attempt and the mirror search) are marked as such where they appear.

A separate agent read the available sources and pre-registered the claims, definitions and tolerances in claims.json before any run. A single agent then built the environment, downloaded and verified the data, and wrote a first report. It could not run the authors' binary, as explained above. A reviewer agent checked that report against the logs, and a reviser agent fixed the issues and added the probes and the reduced-input split in `compare.py`. A last agent installed the same FoldMason release from bioconda, ran the AFDB benchmark and updated this report. A human has to approve publication.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
