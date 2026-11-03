# Blind reread of the Open Tables datasets, November 2026

Every Open Tables dataset is transcribed twice, independently, and every disagreement is settled against the PDF. That leaves one kind of error the method cannot see: the one both transcriptions make the same way. This measurement estimates how much of it is left in the published data.

## How it was measured

- **Sample.** Up to 100 records from each of the 13 published datasets, 1,297 in all, drawn at random with a fixed seed and spread over the documents in proportion to their records (at least one per document while the budget lasted).
- **Blind reading.** For each record a third reader got only what is needed to find the cell (document, page, table, row and column label) and read from the PDF the value, dispersion, significance letter, unit, statistic, stage, year, place, cultivar, dose or species, as the dataset has them. The reader never saw the published record.
- **Judgement.** Every field where the reading and the published record differed was checked again on the page and classed as a published error, a reader error, the same thing in other words, or ambiguous print. Ambiguous print does not count as an error.
- A **value error** is a wrong value, dispersion or significance letter. A **context error** is a field that places or qualifies the value (unit, stage, year, cultivar, species) that is wrong, or empty when the page prints it.

## Result

| Dataset | Records | Value errors | Context errors | Records with an error |
|---|---:|---:|---:|---:|
| Fall armyworm in maize | 100 | 0 | 0 | 0 |
| Rice blast | 100 | 2 | 0 | 2 |
| Soybean rust | 100 | 0 | 0 | 0 |
| Cassava | 99 | 0 | 0 | 0 |
| Wheat | 100 | 0 | 0 | 0 |
| Tomato | 100 | 0 | 0 | 0 |
| Potato | 100 | 0 | 0 | 0 |
| Common bean diseases | 100 | 0 | 2 | 2 |
| Cowpea | 98 | 0 | 9 | 9 |
| Coffee | 100 | 0 | 1 | 1 |
| Biodiversity inventories | 100 | 0 | 0 | 0 |
| Fisheries and aquaculture | 100 | 0 | 1 | 1 |
| Historical public health | 100 | 0 | 0 | 0 |
| **All** | **1,297** | **2** | **13** | **15** |

Per 1,000 records, with a 95% Wilson interval: value errors 1.5 (0.4 to 5.6), context errors 10.0 (5.9 to 17.1), any error 11.6 (7.0 to 19.0). Each dataset weighs about the same in the sample, so this is the rate of the sample, not of all published records; and the errors came in groups (7 of the 9 in cowpea are one table), so the true interval is wider than the one shown.

No number was misread. The 2 value errors are a Dunnett marker ("*" or "ns") printed on the value and kept in `notes` instead of `significance_letter`. The 13 context errors come from 7 decisions, each one a rule both transcriptions read the same wrong way: a stage stated in the methods marked as not printed, a cultivar left empty on a cultivar row, a unit printed in the header left empty, a period given in the text not filled in, and an aggregate row ("Outros") left without its label.

## What was fixed

Because a shared error repeats across a table, each one was fixed for the whole table, not only for the sampled record: 497 cells in 5 datasets, released as new versions; every changed cell is listed in [blind-reread-2026-11-fixes.csv](blind-reread-2026-11-fixes.csv).

- Rice blast (v1.0.1): the Dunnett marker moved to `significance_letter` in the 36 records of prabhu1983.
- Cowpea (v1.0.1): the harvest stage of Table 3 of marinho2014 (112 records), and the cultivar of the cultivar rows of santos1978 Table 1 (24) and cardoso1997 Table 2 (42).
- Common bean diseases (v1.0.1): the units of two columns and the stage of the severity column of sartorato2006 Table 2 (18 records).
- Coffee (v1.0.1): the harvest years of one text record of miranda1999.
- Fisheries and aquaculture (v2.0.1): the label of the 39 "Outros" records of castro2009.

The reader made 290 field errors of its own, almost all because the blind locator lacked the year, sample or period and the row label repeated; every one was settled on the page and none changes the result. The next reread will carry those columns in the locator.
