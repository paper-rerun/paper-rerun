**Overall verdict: sound with corrections.** The "Reproduced" verdict holds: I recomputed all 42 MAEs from the CSVs and every one matches compare.log. Under a tight 5% band applied to all claims, 40 of 42 pass, above the minimum of 38. What needs fixing is several counts in the text, the definition of the 10 eV/Å cut (wrong in the text and in the note to the authors), the note on the stored columns, the OOM note and the licence line.

Scratch in `E:\Ciencia\noturno\2025-kovacs-maceoff\review_scratch\` (recompute.py/.out, recompute2.py/.out, cpu_spot.py/.out, run.sh). CPU only, 4 threads, nice 19. No file in the rerun was altered.

## Findings

**1. blocker (for the note to the authors) / must-fix (in the report): the 10 eV/Å cut is on the largest Cartesian component, not on the magnitude.**
- Text: "Table S1 was computed on a test set filtered at 10 eV/Å on the DFT force magnitude", "a maximum reference force cut of 10 eV/Å" and, in note 1, "A maximum DFT force cut of 10 eV/Å".
- What is wrong: the `ref_max_abs_f_eV_A` column is `np.abs(f_ref).max()` (evaluate.py, in the `w.writerow`), i.e. the max of |F_x|, |F_y|, |F_z| over all atoms. It is not the per-atom norm.
- Evidence (recompute.out and recompute2.out):
  - With the per-atom norm ≤ 10 you get PubChem 33,722, Dimers 13,884 and Dipeptides 1,023, and only 31 of 42 values match.
  - With the component ≤ 10, the window that gives both published counts is [9.9970, 10.0023) eV/Å. It is narrow and centred on 10, so the 10 really does stand out.
  - A per-atom norm ≤ 11.63 also hits both counts, but the set differs by 56 configurations and gives 39 of 42: PubChem F comes out 35.65 / 20.55 / 14.72 against 35.68 / 20.57 / 14.75.
  - So only the component cut at 10 reproduces all 42 values.
- Corrected text: "a cut of 10 eV/Å on the largest absolute Cartesian component of the DFT forces (max over atoms and x, y, z). Any cut in [9.997, 10.002) eV/Å gives both published counts. A cut on the per-atom force norm can also hit both counts (at about 11.63 eV/Å, a non-round value) but then misses three PubChem force values (35.65, 20.55, 14.72), so the component cut is the one consistent with Table S1."
- Note 1 to the authors has to say "largest Cartesian component". If it does not, anyone checking with the norm will find 33,722 and conclude we are wrong.

**2. must-fix: A2 is not the filter from issue #7, and the word "magnitude" is wrong.**
- Text: "dropping configurations whose reference forces have a maximum magnitude above 15 eV/Å or a net force above 0.1 eV/Å removes 94 PubChem configurations". In claims.json, A2 appears as "the filters issue #7 points at".
- What is wrong: compare.py uses the component column (`a[:,4] <= 15`). Issue #7 uses the per-atom norm (`> 15`).
- Evidence:
  - With the norm, 126 PubChem configurations drop out, exactly the issue's number. With the component, 94 drop out.
  - With the norm, PubChem gives 1.412 / 35.732 (23S), 0.910 / 20.612 (23M) and 0.888 / 14.787 (23L).
- Corrected text: "...whose largest reference force component exceeds 15 eV/Å... removes 94 PubChem configurations. With the per-atom norm, as in issue #7, it removes 126 (the issue's number) and gives 1.412/35.732, 0.910/20.612, 0.888/14.787. Neither reaches the published values."

**3. must-fix: summary counts that come from no log.**
- "36 of them within 0.5%": the right number is **34**. Outside 0.5% are the three PubChem E values, E-23L Dimers (+1.00%), E-23L Dipeptides (−1.10%) and the three PubChem F values.
- "Every other number sits within 0.5%" and "The only deviations above 1% are the two subsets whose released set is larger" are both wrong: E-23L-Dipeptides gives −1.10% (compare.log), and Dipeptides has the same count as the paper.
- "20 of them agree to all printed digits": that number appears in no log. Rounded to two decimals, 32 match (the 30 from the five subsets plus E-23S/23M Dimers). Only 3 match already at three decimals.
- Corrected text: "34 of them within 0.5%... Outside PubChem and DES370K Dimers every number is within 0.5% except 23L Dipeptides energy (0.415 vs 0.42, −1.1%), which still rounds to the published 0.42. 32 of the 42 round to the published value."

**4. must-fix: the wide band was chosen to absorb a discrepancy we already knew about.**
- Text: "All 42 pre-registered claims fall inside their bands", repeated at the end as "fixed before running, on the ground that...".
- What is wrong: the band was indeed fixed before the run (freeze at 21:26:03Z; the first model ran at 21:42Z in the speedtest and at 21:43:19Z in run_all; the weights only arrived at 21:27Z). But claims.json itself justifies the 15% band with the +209/+12 from issue #7 and the "126 ... failing". It was designed to swallow that difference, and 2 of the 12 wide-band claims only pass because of it: F-23M PubChem +5.23% and F-23L PubChem +7.24%.
- Corrected text, in the summary: "42 of 42 inside their pre-registered bands; 40 of 42 under the 5% band applied to every subset. The two that need the wider band (PubChem force, 23M +5.2% and 23L +7.2%) were given it because we already knew from issue #7 that the released PubChem set is larger than the paper's, so those two passes are not independent agreement." The verdict stays Reproduced.

**5. must-fix: the version-of-record SI exists, and equivalence with v5 was not verified.**
- Text: "The published SI is not reachable". In claims.json: "whose SI section S2 and Table S1 are the SI of the published paper".
- Evidence:
  - PMC hosts the VoR SI: `paper/fulltext.xml` and `pmc12123624.html` point to `/articles/instance/12123624/bin/ja4c07099_si_001.pdf` (853,967 bytes). It sits behind a browser challenge (the fetch got "Preparing to download"), and Europe PMC answers 403.
  - The arXiv v4 PDF (2025-04-12, before publication) carries no SI at all. Table S1 cannot be compared across arXiv versions starting from v4. v1 to v3 were not checked.
  - Table 1 matches (33,884 / 13,896) in v4, in v5 and in PMC.
- Corrected text: "The version-of-record SI is listed in PMC (ja4c07099_si_001.pdf, 853,967 bytes) but sits behind a browser check we did not pass; we read Table S1 from arXiv v5 and have not confirmed it is identical to the published SI. arXiv v4 carries no SI." I recommend Filipe open the PMC PDF in a browser and compare the 42 cells before publishing.

**6. must-fix: stored columns.**
- Text (note 3): "so they are not the output of any released checkpoint. We take them to be the screening model of SI S1." In the results: "They look like the screening model the SI mentions".
- What is wrong:
  - The pinned commit also publishes `mace_off23/MACE-OFF23b_medium.model` (line 4 of weights_blob_sha.log), and it was not evaluated. There is also `mace_off24/`, but the 2023-05-23 mtime inside the tar argues against the 24.
  - The SI says screening used the *small* model ("After fitting the small MACE model..."). A small model with an energy error of 0.835, lower than the 23L's 0.912, contradicts the "screening model" hypothesis.
- Corrected text: "...not the output of 23S, 23M or 23L (23b_medium, also in the repository, was not tested). Nothing in the archive says what wrote them." The "screening model" sentence has to go.
- I checked the parse in stored_mace_columns.py: the 50,195 Properties lines are identical and columns 4:7 / 7:10 are right.

**7. must-fix: note 6 to the authors is contradicted by our own logs.**
- Text: "MACE-OFF23(L) in float64 will not score a 150-atom water cluster inside 4 GB of VRAM at batch size 2."
- Evidence: the resumed run started exactly on the 150-atom water that killed attempt 2 (index 18,507). It scored it on the GPU with fraction 0.5 and `expandable_segments`, with no OOM or CPU line anywhere in eval_large.log. The problem was fragmentation, not capacity.
- The sentence "float32 is not an option" is an argument, not a measurement.
- Fix: drop note 6. If something should stay: "with expandable_segments, 4 GB was enough for every configuration."

**8. must-fix: licence.**
- Text: "Filipe Tessaro accepted it on 2026-11-08 before the download; this agent accepted nothing."
- What is wrong: the README says "By Downloading the models you agree to the Academic Software License", and the download was done by the agent (download_weights.log, 21:27Z).
- Corrected text: "Filipe Tessaro accepted the ASL on 2026-11-08; the agent downloaded the weights on his instruction under that acceptance and accepted no licence of its own. The weights are not redistributed with this report; outputs derived from them are for academic non-commercial use only."
- The `weights/` folder must not go into the public repository.
- For Filipe, not for the report: the ASL defines academic use as research "undertaken at an educational, non-profit, charitable or governmental institution" (LICENSE.md, line 75). A run at home, by a private individual, may not qualify. He has to decide that before publishing.

**9. minor: the headline claims more than the evidence supports.**
- Text: "We also found what explains issue #7". The "How this report was made" section itself says the finding still needs the blind recount.
- Corrected text: "We found a cut that is consistent with issue #7".

**10. minor: wording of the notes to the authors.**
- Note 1: post it as a comment on issue #7, which is still open and unanswered. I opened it today: zero comments, no maintainer replied, and nothing in the paper, the SI, the README or the issue mentions 10 eV/Å. Worth saying that the issue's 126 come from the per-atom norm filter, and that the 94 from the component cut are purely a matter of definition.
- Note 2: "neither Apollo file contains them" was not verified for the training archive (`train_large_neut_no_bad_clean.tar.gz`), which was not downloaded. Change to: "the test archive does not contain them (the paper uses them for testing only)".
- Notes 4 and 5: little value to the authors. I suggest cutting 4 and shortening 5.
- None of issues #1 to #8 already covers notes 1 to 3, so they are new.

**11. minor: small inconsistencies.**
- compare.log prints F-23L Monomers as 6.575; the real value is 6.5755, which the report shows as 6.576. It comes from double rounding in `round(...,4)` followed by `.3f`.
- In the 10 eV/Å cut table, E-23L Dimers shows as "0.545", but the real value is 0.544743, which rounds to 0.54. Show four decimals.
- frozen_at in claims.json says 21:26:00Z; claims.frozen_at.txt says 21:26:03Z.
- "GPU sat at 96%" and "under a minute" appear in no log.
- "about 5 h" of wall clock actually adds up to 4h33 (2:01 + 1:44:50 + 2:45:54).
- claims.json promised to report the per-snapshot split question from issue #7 ("reported as a finding, not scored"), and REPORT.md says nothing about it.

## What I checked and found correct

- The SHA-256 of claims.json matches the .sha256. The freeze (21:26Z) came before the weights download (21:27Z), the speedtest and run_all (21:42–21:43Z). The switch from Table 1 to Table S1 is recorded in the frozen claims.json.
- The 42 paper values in claims.json match Table S1 of arXiv v5.
- The 42 recomputed MAEs match compare.log. The report's table checks out (apart from 6.575/6.576). The 30 values from the five subsets with matching counts agree to both printed decimals.
- Units: energy is the mean of |ΔE|/N_atoms in meV/atom and force is the per-component MAE in meV/Å. The vector-norm version is about 2× and does not match. The SI does not define this explicitly (Eq. 6 is ambiguous); the choice is justified empirically.
- The counts (34,093 / 13,908 etc.) and the cut sweep match my independent parse of the xyz. The reference-maximum column in the CSV is identical to the one I pulled from the xyz (difference 0.0). With a component cut ≤ 10, all 42 values reproduce Table S1 to both decimals.
- errors_large.csv has 50,195 rows, indices 0 to 50,194, no duplicates, no gaps, no truncated rows. The splice at 18,506/18,507 is clean. The same holds for small and medium.
- No CPU fallback in the final run. In the CPU spot check with `MACECalculator` (an independent code path), in float64, the small model on 51 configurations and the large on 7 (including 18,505–18,508) match the rows written on the GPU to within 1e-12 eV/atom and 1e-13 eV/Å. CPU and GPU do not change the result.
- The OOM narrative matches the logs: attempt 2 hit `OutOfMemoryError` in the batch, and the single-configuration retry raised a `RuntimeError` coming from TorchScript. The `/usr/bin/time` figures (14:39, 1:01:00, 2:45:54) and the RSS peaks check out.
- The weights checksum list checks out. The licence line carries the non-commercial restriction (adjust the wording per finding 8).
- REPORT.md mentions no heredoc and no refused Write, so there is nothing to check there.
