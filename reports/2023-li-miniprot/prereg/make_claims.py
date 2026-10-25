# Builds claims.json for the miniprot Table 1 pre-registration. Run once, then freeze
import json

CREATED = "2026-10-25T11:37:09-03:00"
OUT = "/mnt/e/Ciencia/noturno/2023-li-miniprot/claims.json"

GENCODE41 = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_41/"
GENCODEM30 = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M30/"
ENS107 = "https://ftp.ensembl.org/pub/release-107/"
METAZOA54 = "https://ftp.ensemblgenomes.ebi.ac.uk/pub/metazoa/release-54/"

HUMAN_GENOME = GENCODE41 + "GRCh38.primary_assembly.genome.fa.gz"
HUMAN_GTF = GENCODE41 + "gencode.v41.annotation.gtf.gz"
FLY_GENOME = ENS107 + "fasta/drosophila_melanogaster/dna/Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz"
FLY_GTF = ENS107 + "gtf/drosophila_melanogaster/Drosophila_melanogaster.BDGP6.32.107.gtf.gz"
ZF_PEP = ENS107 + "fasta/danio_rerio/pep/Danio_rerio.GRCz11.pep.all.fa.gz"
MM_PEP = GENCODEM30 + "gencode.vM30.pc_translations.fa.gz"
MM_GTF = GENCODEM30 + "gencode.vM30.annotation.gtf.gz"
AG_PEP = METAZOA54 + "fasta/anopheles_gambiae/pep/Anopheles_gambiae.AgamP4.pep.all.fa.gz"

COLUMNS = {
	"zf_hs_j2": {
		"label": "zebrafish->human, miniprot, splice model 'human' (-j2)",
		"table_column": "Table 1, column 1 (Genome human / Protein zebrafish / Aligner miniprot / Splice model human)",
		"aligner_cmd": "miniprot -t16 -j2 GRCh38.primary_assembly.genome.fa.gz zebrafish.longest.faa > zf_hs_j2.paf",
		"genome": HUMAN_GENOME,
		"proteins": "test set TS-ZF (see definitions)",
		"annotation": HUMAN_GTF,
		"values": [25007, 16866, 157918, 482, 145545, 92.16, 63.11, 95.43],
		"notes": {"elapsed_s": 267, "peak_ram_gb": 21.8},
		"unpublished_commented_rows": {"mapped": 20381, "single_exon": 3515},
	},
	"zf_hs_j1": {
		"label": "zebrafish->human, miniprot, splice model 'general' (-j1)",
		"table_column": "Table 1, column 2 (Genome human / Protein zebrafish / Aligner miniprot / Splice model general)",
		"aligner_cmd": "miniprot -t16 -j1 GRCh38.primary_assembly.genome.fa.gz zebrafish.longest.faa > zf_hs_j1.paf",
		"genome": HUMAN_GENOME,
		"proteins": "test set TS-ZF (see definitions)",
		"annotation": HUMAN_GTF,
		"values": [25007, 17104, 161295, 802, 144734, 89.73, 63.16, 94.91],
		"notes": {"elapsed_s": 257, "peak_ram_gb": 22.5},
		"unpublished_commented_rows": {"mapped": 20392, "single_exon": 3288},
	},
	"mm_hs_j2": {
		"label": "mouse->human, miniprot, splice model 'human' (-j2)",
		"table_column": "Table 1, column 7 (Genome human / Protein mouse / Aligner miniprot / Splice model human)",
		"aligner_cmd": "miniprot -t16 -j2 GRCh38.primary_assembly.genome.fa.gz mouse.testset.faa > mm_hs_j2.paf",
		"genome": HUMAN_GENOME,
		"proteins": "test set TS-MM (see definitions)",
		"annotation": HUMAN_GTF,
		"values": [21844, 17065, 167446, 330, 162675, 97.15, 90.10, 97.26],
		"notes": {"elapsed_s": 164, "peak_ram_gb": 15.3},
		"unpublished_commented_rows": {"mapped": 20469, "single_exon": 3404},
	},
	"ag_dm_j2": {
		"label": "mosquito->fruit fly, miniprot, splice model 'human' (-j2), max intron 50 kb (-G 50k)",
		"table_column": "Table 1, column 9 (Genome fruit fly / Protein mosquito / Aligner miniprot / Splice model human)",
		"aligner_cmd": "miniprot -t16 -j2 -G 50k Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz mosquito.longest.faa > ag_dm_j2.paf",
		"genome": FLY_GENOME,
		"proteins": "test set TS-AG (see definitions)",
		"annotation": FLY_GTF,
		"values": [13094, 6675, 22614, 488, 19774, 87.44, 56.10, 96.69],
		"notes": {"elapsed_s": 34, "peak_ram_gb": 3.9},
		"unpublished_commented_rows": {"mapped": 8827, "single_exon": 2152},
	},
}

QUANTITIES = [
	("n_proteins", "# proteins", "count", False),
	("n_multi_exon", "# multi-exon", "count", False),
	("n_pred_junc", "# predicted junc.", "count", False),
	("n_nonovlp_junc", "# non-ovlp. junc.", "count", False),
	("n_confirmed_junc", "# confirmed junc.", "count", False),
	("pct_confirmed_junc", "% confirmed junc.", "percent", True),
	("pct_base_sn", "% base SN", "percent", True),
	("pct_base_sp", "% base SP", "percent", True),
]

SOURCE_OF_VALUE = {
	"n_proteins": "number of sequences in the query FASTA of the test set (D-TESTSET-*)",
	"n_multi_exon": "junceval line '# mapped reads' minus line '# singletons' (D-MULTIEXON)",
	"n_pred_junc": "junceval line '# predicted introns'",
	"n_nonovlp_junc": "junceval line '# non-overlapping introns'",
	"n_confirmed_junc": "junceval line '# correct introns' (the count)",
	"pct_confirmed_junc": "junceval line '# correct introns' (the percentage in parentheses, toFixed(2))",
	"pct_base_sn": "exoneval -s line 'Base Sn' (percentage, toFixed(2))",
	"pct_base_sp": "exoneval -s line 'Base Sp' (percentage, toFixed(2))",
}

TOL_PCT = {
	"tolerance": "abs(ours - paper) <= 0.50 percentage points",
	"basis": (
		"miniprot and paftools are deterministic, so with identical inputs the expected difference is 0 "
		"(only rounding, 0.005 pp). The paper does not publish the protein id lists or the evaluation "
		"command line, so the inputs are reconstructed: the zebrafish and mouse test sets differ by about "
		"0.35% of proteins from the paper's counts (triage 2026-10-25: 25,094 vs 25,007; 21,919 vs 21,844 "
		"under the longest-per-gene rule). If a fraction d of proteins is swapped and those proteins were "
		"all wrong (worst case), a junction or base percentage moves by at most about 2*d*100% = 0.7 pp; "
		"realistic swaps of mostly ordinary genes move it far less. 0.50 pp is set below that worst case "
		"and is applied to all 12 percentages, including mosquito (exact count but unpublished id list and "
		"unpublished 'longest transcript' filter for base SN/SP). No author per-item data exist to "
		"bootstrap a tolerance. The report also flags whether each value matches exactly (|diff| < 0.01 pp)."
	),
}
TOL_COUNT = {
	"tolerance": "abs(ours - paper) / paper <= 1%",
	"basis": "Check only, not a primary claim. Same reasoning as the percentages: test set reconstructed with ~0.35% count deviation; 1% relative allows that plus knock-on effects. Deviation is reported exactly.",
}
TOL_NONOVLP = {
	"tolerance": "abs(ours - paper) / paper <= 10%",
	"basis": "Check only. Small counts (330 to 802) where a few dozen swapped proteins move the number by several percent; reported exactly.",
}
TOL_NPROT = {
	"tolerance": "reported exactly, no pass/fail",
	"basis": "Determined by the pre-registered test-set rule, not by the method. The report states the deviation (triage: mosquito exact, zebrafish +87 under rule TS-ZF, mouse unknown under rule TS-MM).",
}

claims = []
for col_id, col in COLUMNS.items():
	for (q_id, q_label, unit, primary), value in zip(QUANTITIES, col["values"]):
		if q_id == "n_proteins":
			tol = TOL_NPROT
		elif q_id == "n_nonovlp_junc":
			tol = TOL_NONOVLP
		elif unit == "count":
			tol = TOL_COUNT
		else:
			tol = TOL_PCT
		claims.append({
			"id": col_id + "." + q_id,
			"role": "primary" if primary else "check",
			"quantity": q_label,
			"paper_value": value,
			"paper_value_text": (f"{value:,}" if unit == "count" else f"{value:.2f}%"),
			"unit": unit,
			"location": col["table_column"] + ", row '" + q_label + "'; Bioinformatics 39(1) btad014, identical in tex/miniprot.tex and arXiv 2210.08052v2",
			"tolerance": tol["tolerance"],
			"tolerance_basis": tol["basis"],
			"how_obtained": SOURCE_OF_VALUE[q_id],
			"conditions": {
				"column": col["label"],
				"aligner": "miniprot 0.7-r207 (tag v0.7, commit 2e57d1a735097f5a95ca71885181ffd7dae4c865), prebuilt miniprot-0.7_x64-linux binary from the release page",
				"aligner_command": col["aligner_cmd"],
				"genome": col["genome"],
				"query_proteins": col["proteins"],
				"evaluation_annotation": col["annotation"],
				"evaluation_commands": "see D-EVAL-JUNC and D-EVAL-BASE",
				"evaluator": "paftools.js from lh3/minimap2 commit 822ccd173358f11842b6dc54e17bbdcc2d9a0a9a (r1152), run with k8 1.2",
				"model_checkpoint_samples": "not applicable: deterministic aligner, no trained weights, no random seed",
			},
		})

notes = []
for col_id, col in COLUMNS.items():
	notes.append({
		"id": col_id + ".notes",
		"elapsed_time_s": col["notes"]["elapsed_s"],
		"peak_ram_gb": col["notes"]["peak_ram_gb"],
		"status": "note only, not a claim: machine dependent and the thread count is not stated in the paper",
	})
	notes.append({
		"id": col_id + ".commented_rows",
		"mapped": col["unpublished_commented_rows"]["mapped"],
		"single_exon": col["unpublished_commented_rows"]["single_exon"],
		"status": "rows '%\\# mapped' and '%\\# single-exon' are commented out in tex/miniprot.tex and absent from the published table. Not claims. Used only to read the definition of '# multi-exon' (mapped - single_exon = multi-exon holds for all four columns). Reported for information.",
	})

definitions = [
	{
		"id": "D-VERSION",
		"choice": "miniprot 0.7-r207. Main run uses the prebuilt release binary miniprot-0.7_x64-linux.tar.bz2 (check that 'miniprot --version' prints 0.7-r207). Building from source at the tag is a variant only if the binary fails.",
		"quote": "\"Only miniprot-0.7, Spaln2-2.4.13c, GeMoMa-1.9 GenomeThreader-1.7.3 could finish the alignment in an hour.\" (Results, Evaluated tools)",
		"ambiguity": "tex/miniprot.tex at tag v0.7 still says 'miniprot-0.6'; it was changed to 'miniprot-0.7' on 2022-12-28 ('fixed a couple of typos'), and the arXiv v2 source and the published paper say 0.7. The table is byte-identical across the three versions. README on master: 'the published paper evaluated miniprot-0.7'.",
	},
	{
		"id": "D-SPLICE",
		"choice": "Splice model 'human' = -j2, 'general' = -j1. All other miniprot options at 0.7 defaults (-G 200k, --outs 0.99, --outn 1000, -N 30, -p 0.5), except -G 50k for mosquito->fly. Output format: default PAF (no --gff). Threads: -t16.",
		"quote": "Table 1 row 'Splice model: human | general'; \"Our human splice model considers these signals. It is also applicable to species with the sequence features above, including Drosophila.\"; \"Miniprot finds introns up to 200 kbp in length by default. We changed this value to 50 kbp for fly-mosquito alignment.\"",
		"ambiguity": "The paper never prints a miniprot command line. In 0.7, -j takes 2=mammal, 1=general (default 1), 0=none (options.c sp_model = NS_S_GENERIC; man page). Thread count is not stated; miniprot output is expected not to depend on -t, which is assumed, not tested by the paper. PAF vs --gff: paftools junceval/exoneval -a read both (##PAF lines), so results are the same.",
	},
	{
		"id": "D-GENOME",
		"choice": "Human: Gencode v41 GRCh38.primary_assembly.genome.fa.gz (" + HUMAN_GENOME + "), used as distributed, contig order unchanged. Fly: Ensembl 107 Drosophila_melanogaster.BDGP6.32.dna.toplevel.fa.gz (" + FLY_GENOME + "), unmasked, order unchanged. Verify against Gencode MD5SUMS and Ensembl CHECKSUMS.",
		"quote": "\"We mapped zebrafish and mouse proteins to the primary assembly of the human reference genome GRCh38 and mapped mosquito proteins to the Drosophila BDGP6 genome.\"",
		"ambiguity": "The paper does not name the FASTA file. Gencode's primary assembly FASTA is chosen because its contig names (chr1...) match the Gencode v41 GTF used for evaluation; Ensembl's GRCh38 primary assembly uses '1' and would not match. The fly file is not named either; Ensembl 107 is the release the paper cites for fly annotation, and toplevel = primary for BDGP6 (no ALT). Contig order changes tie-breaking (miniprot issue #79), so files are never reordered or filtered.",
	},
	{
		"id": "D-TESTSET-ZF",
		"choice": "TS-ZF: from Ensembl 107 Danio_rerio.GRCz11.pep.all.fa.gz (" + ZF_PEP + "), keep records whose header has gene_biotype:protein_coding and whose location is on coordinate system 'chromosome' with name 1..25 (excludes MT, unplaced scaffolds and CHR_ALT haplotypes); group by the 'gene:' id; keep the longest sequence (aa length), ties to the first record in file order; write selected records in original file order, sequence unchanged, name = first header token. Triage count under this rule: 25,094 (paper 25,007, +87, +0.35%).",
		"quote": "\"zebrafish (Danio rerio) and fruit fly (Drosophila melanogaster) from Ensembl v107 ... We selected the longest protein for each gene to reduce redundant sequences.\"",
		"ambiguity": "No id list is published and no filter tried in triage (ALT, MT, scaffolds, X, internal stop, duplicate sequence, min length) gives 25,007 exactly. The literal reading (all genes in pep.all) gives a larger set; README at tag v0.7 used 29,706 'longest proteins per gene' for fish with an earlier version, so the paper's set was filtered further in an unstated way. The closest documented rule is fixed here and the count deviation is reported. Variants under Alternative readings.",
	},
	{
		"id": "D-TESTSET-MM",
		"choice": "TS-MM: Ensembl canonical mouse proteins from Gencode M30. Take every 'transcript' line of gencode.vM30.annotation.gtf.gz (" + MM_GTF + ") with tag \"Ensembl_canonical\"; keep those whose transcript_id (with version) is the 2nd '|' field of a header in gencode.vM30.pc_translations.fa.gz (" + MM_PEP + "); output that translation, in pc_translations file order, name = first '|' field (ENSMUSP id). No gene_type or chromosome filter.",
		"quote": "Paper: \"mouse (Mus musculus) from Gencode M30 ... We selected the longest protein for each gene to reduce redundant sequences.\" README.md at tag v0.7 (Evaluation): \"We collected Ensembl canonical mouse proteins from Gencode vM30 and longest proteins per gene for chicken and zebrafish (fish).\"",
		"ambiguity": "The paper says 'longest protein for each gene' for all species, but the README at the same release tag describes the mouse set as Ensembl canonical proteins, and its table reports the same 21,844 mouse proteins and the identical Spaln2 mouse numbers as the paper (171,241 / 852 / 162,551 / 94.93%). So the paper's mouse set is the README's set, and the author's own README names the selection. This was decided from the two author texts, not from any count we computed. Triage's longest-per-protein_coding-gene rule (21,919, +0.34%) is kept as variant MM-A. The canonical set's size is not known yet and its deviation from 21,844 will be reported.",
	},
	{
		"id": "D-TESTSET-AG",
		"choice": "TS-AG: from Ensembl Metazoa 54 Anopheles_gambiae.AgamP4.pep.all.fa.gz (" + AG_PEP + "), all records, group by 'gene:' id, keep the longest (aa), ties to the first in file order, output in original file order, name = first header token. Triage count: 13,094 (paper 13,094, exact).",
		"quote": "\"mosquito (Anopheles gambiae) from Ensembl metazoan v54. We selected the longest protein for each gene\"",
		"ambiguity": "Count matches exactly, but which isoform wins a tie is not stated. Ties to first-in-file is our choice.",
	},
	{
		"id": "D-EVAL-JUNC",
		"choice": "k8 paftools.js junceval -a -1 <annotation GTF> <miniprot PAF>, with -l 0 (default, exact) and without -c. Annotation = the full GTF as distributed: human gencode.v41.annotation.gtf.gz (" + HUMAN_GTF + "), fly Drosophila_melanogaster.BDGP6.32.107.gtf.gz (" + FLY_GTF + "). junceval builds introns from all 'exon' lines of every transcript (coding and non-coding).",
		"quote": "Table 1 legend: \"A splice junction (junc.) is confirmed if it is annotated in 'Genome species' with exact boundaries; is non-overlapping (non-ovlp.) if the intron in the junction is not overlapping with annotated introns. '% confirmed junc.' is the percentage of predicted junctions that are confirmed.\"",
		"ambiguity": "The command line is not published. paftools r1152 prints exactly these quantities ('# predicted introns', '# non-overlapping introns', '# correct introns (x%)'), so it is the evaluator. '-l 0' follows from 'exact boundaries'. '-c' (only chr1-22/X/Y) is not mentioned and would drop fly 2L/2R/3L/3R, so it is off. '-1' (first alignment per protein) is chosen because the legend counts proteins ('# multi-exon gives the number of proteins mapped with multiple exons') and the GeMoMa text evaluates 'the best unfiltered alignment of each protein'; miniprot 0.7 PAF has no tp:A tag, so without -1 every alignment within 0.99 of the best counts as primary. Which Gencode GTF ('annotation' = comprehensive on reference chromosomes vs 'primary_assembly.annotation' vs 'basic') is not stated; the comprehensive reference-chromosome file is the default Gencode download. Variants under Alternative readings.",
	},
	{
		"id": "D-MULTIEXON",
		"choice": "# multi-exon = junceval '# mapped reads' - '# singletons' (with -1, this is the number of proteins whose first alignment has at least one intron).",
		"quote": "\"'# multi-exon' gives the number of proteins mapped with multiple exons.\"",
		"ambiguity": "Not printed directly by paftools. The commented-out rows '# mapped' and '# single-exon' in the author's tex satisfy mapped - single-exon = multi-exon in all four miniprot columns (20,381-3,515=16,866; 20,392-3,288=17,104; 20,469-3,404=17,065; 8,827-2,152=6,675), which fixes the formula from author numbers. '# mapped' = proteins with any mapped signal (lh3 in issue #11).",
	},
	{
		"id": "D-EVAL-BASE",
		"choice": "k8 paftools.js exoneval -a -s -1 <longest-transcript CDS GTF> <miniprot PAF> (-a forces CDS lines). Reference GTF = the evaluation GTF of D-EVAL-JUNC reduced to one transcript per gene: among transcripts with at least one CDS line, the one with the largest summed CDS length (sum of end-start+1 over its CDS lines; stop_codon lines not counted, as in the GTFs), ties to the first transcript in file order; keep only that transcript's CDS lines, unchanged. No gene biotype filter.",
		"quote": "Table 1 legend: \"Base sensitivity (base SN) is the fraction of annotated coding regions on the longest transcripts that are covered by alignments. Base specificity (base SP) is the fraction of genomic bases in alignments that are covered by annotated coding regions.\"",
		"ambiguity": "'Longest transcript' is not defined (CDS length vs spliced mRNA length vs genomic span) and the script that made the reduced GTF is not published. Longest CDS is chosen to mirror how the query proteins were chosen ('longest protein for each gene'). exoneval merges all reference and predicted intervals per contig before computing Sn/Sp (base Sn = covered annotated CDS bases / annotated CDS bases; base Sp = alignment bases on annotated CDS / alignment bases); alignments on contigs absent from the GTF do not enter base Sp. Base SP's 'annotated coding regions' could also mean all CDS, not only the longest transcripts; kept as variant.",
	},
	{
		"id": "D-ROUNDING",
		"choice": "Compare the percentages exactly as printed by paftools (toFixed(2)) to the paper's two-decimal values. Counts compared as integers.",
		"quote": "Table 1 reports percentages with two decimals.",
		"ambiguity": "None beyond rounding.",
	},
	{
		"id": "D-EVALUATOR-VERSION",
		"choice": "paftools.js at minimap2 commit 822ccd173358f11842b6dc54e17bbdcc2d9a0a9a (2022-11-02, r1152, 'evaluate base Sn and Sp'), k8 1.2 (Zenodo 11357203).",
		"quote": "No version is given in the paper; README at tag v0.7 links paftools.js from minimap2 master.",
		"ambiguity": "r1152 is the first version that prints base Sn/Sp and was current until 2023-01-06 (next change to paftools.js: 'removed debugging code'), so it covers the paper's revision date (2022-12-26/28). k8 version is not stated.",
	},
	{
		"id": "D-SCOPE",
		"choice": "Only the four miniprot-0.7 columns. Spaln2, GeMoMa and MetaEuk columns are out of scope. Elapsed time and peak RAM are recorded as notes.",
		"quote": "Table 1 rows 'Elapsed time (sec)' and 'Peak RAM (GB)'.",
		"ambiguity": "Hardware and thread count are not stated, so time and RAM are not comparable claims.",
	},
]

alternatives = [
	{"id": "ALT-1", "what": "junceval and exoneval without -1 (all output alignments counted)", "applies_to": "all 4 columns"},
	{"id": "ALT-2", "what": "junceval and exoneval with -c (only chr1-22, X, Y)", "applies_to": "3 human columns only (fly contigs 2L/2R/3L/3R would be dropped)"},
	{"id": "ALT-3", "what": "junceval with -l 1 and with -l 3", "applies_to": "all 4 columns, junction rows only"},
	{"id": "ALT-1x2", "what": "combinations of ALT-1 and ALT-2 (no -1 with -c)", "applies_to": "3 human columns"},
	{"id": "ALT-4", "what": "exoneval reference = all CDS lines of the GTF (no longest-transcript reduction)", "applies_to": "base SN/SP"},
	{"id": "ALT-5", "what": "longest transcript by spliced exon length among CDS-bearing transcripts (CDS lines of that transcript)", "applies_to": "base SN/SP"},
	{"id": "ALT-6", "what": "longest-CDS reduction restricted to gene_type/gene_biotype protein_coding", "applies_to": "base SN/SP"},
	{"id": "ALT-7", "what": "human evaluation GTF = gencode.v41.primary_assembly.annotation.gtf.gz, and separately gencode.v41.basic.annotation.gtf.gz", "applies_to": "3 human columns"},
	{"id": "ALT-ZF-A", "what": "TS-ZF literal: longest protein per gene over all of pep.all (any biotype, any region)", "applies_to": "zebrafish columns"},
	{"id": "ALT-ZF-B", "what": "TS-ZF plus MT; and protein_coding on all regions incl. scaffolds, excluding CHR_ALT", "applies_to": "zebrafish columns"},
	{"id": "ALT-ZF-C", "what": "TS-ZF with transcript_biotype:protein_coding required for the chosen isoform", "applies_to": "zebrafish columns"},
	{"id": "ALT-MM-A", "what": "TS-MM as longest translation per gene among gene_type protein_coding genes with CDS in the M30 GTF (triage: 21,919)", "applies_to": "mouse column"},
	{"id": "ALT-MM-B", "what": "TS-MM canonical restricted to gene_type protein_coding", "applies_to": "mouse column"},
	{"id": "ALT-BIN", "what": "miniprot built from source at tag v0.7 instead of the prebuilt binary (only if outputs differ or the binary fails)", "applies_to": "all"},
	{"id": "ALT-T", "what": "-t4 (miniprot default) instead of -t16 on the mosquito column, to check thread independence", "applies_to": "mosquito column"},
]

doc = {
	"stage": "pre-registration",
	"created": CREATED,
	"paper": {
		"citation": "Li, H. Protein-to-genome alignment with miniprot. Bioinformatics 39(1), btad014 (2023)",
		"doi": "10.1093/bioinformatics/btad014",
		"pmid": "36648328",
		"preprint": "arXiv:2210.08052v2 (28 Dec 2022, same Table 1)",
		"code": "https://github.com/lh3/miniprot @ v0.7 = 2e57d1a735097f5a95ca71885181ffd7dae4c865",
	},
	"target": "Table 1, the four miniprot-0.7 columns (zebrafish->human -j2, zebrafish->human -j1, mouse->human -j2, mosquito->fly -j2 -G 50k)",
	"sources_read": [
		{"file": "paper/miniprot.tex.master", "what": "tex/miniprot.tex on master (81f9b93), Table 1 = published", "sha256": "8cb6ea02433c12a25bcbc5867e85f370d1811175a5f46c5901ca8786c5da643d"},
		{"file": "paper/miniprot.tex.2e57d1a735097f5a95ca71885181ffd7dae4c865", "what": "tex/miniprot.tex at tag v0.7, identical table", "sha256": "a3ac506bb04d8ef963e390df755740c3b710a182d4d37e4ab9fd7aa0d3b6dfc0"},
		{"file": "paper/arxiv_v2/src.bin", "what": "arXiv 2210.08052v2 source, identical table", "sha256": "c23694febc62c203890d5d6709601dbb9ea6df41bf0e75cd3c360cd1450a9df4"},
		{"file": "paper/README.v0.7.md", "what": "README.md at tag v0.7 (older evaluation section)", "sha256": "2d1bde907ddec5475fb80f6d2a6b0d6ab6d674d5e1efcf415d5a0d46d86bd2c5"},
		{"file": "paper/paftools.js.822ccd1", "what": "minimap2 misc/paftools.js at r1152", "sha256": "2e85a21498c057cb1b617cbd908b2a55e9eae4ffb116aa9991c58ea2bb052206"},
	],
	"supplementary_and_author_per_item_data": "None. No supplement, no per-protein results, no id lists. sources/ is left empty. The only author numbers beyond Table 1 are the two commented-out rows in the tex and the older README table (different miniprot version), used only to read definitions.",
	"claims": claims,
	"notes_not_claims": notes,
	"definitions": definitions,
	"alternative_readings": {
		"rule": "Computed only after the main result for all four columns is final. Reported under 'Alternative readings', never used for the verdict.",
		"variants": alternatives,
	},
	"verdict_rule": "Reproduced: all 12 primary percentages within 0.50 pp under the main definitions. Partially reproduced: some within, some not. Not reproduced: none within. Count checks and test-set deviations are reported next to the verdict and do not change it.",
}

with open(OUT, "w", newline="\n") as f:
	json.dump(doc, f, indent=2, ensure_ascii=False)
	f.write("\n")
print(len(claims), "claims written")
