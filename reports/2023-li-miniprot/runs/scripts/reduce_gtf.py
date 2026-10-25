# Reduce a GTF to the CDS lines of one transcript per gene, for exoneval base Sn/Sp.
# Modes:
#   longest_cds     main (D-EVAL-BASE): largest summed CDS length among CDS-bearing transcripts
#   longest_spliced ALT-5: largest summed exon length among CDS-bearing transcripts
#   longest_cds_pc  ALT-6: longest_cds restricted to protein_coding genes
# Ties go to the first transcript in file order. CDS lines are written unchanged.
# Usage: python3 -I reduce_gtf.py <mode> <in.gtf.gz> <out.gtf>
import gzip
import re
import sys


def main():
	mode, in_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

	transcript_order = []
	gene_of_transcript = {}
	cds_length = {}
	exon_length = {}
	cds_lines = {}
	gene_is_protein_coding = {}

	with gzip.open(in_path, "rt") as handle:
		for line in handle:
			if line.startswith("#"):
				continue
			fields = line.split("\t")
			feature = fields[2]
			if feature not in ("CDS", "exon"):
				continue
			attributes = fields[8]
			transcript_match = re.search(r'transcript_id "([^"]+)"', attributes)
			if transcript_match is None:
				continue
			transcript_id = transcript_match.group(1)
			gene_id = re.search(r'gene_id "([^"]+)"', attributes).group(1)
			if transcript_id not in gene_of_transcript:
				gene_of_transcript[transcript_id] = gene_id
				transcript_order.append(transcript_id)
				cds_length[transcript_id] = 0
				exon_length[transcript_id] = 0
			# Gencode uses gene_type, Ensembl uses gene_biotype
			type_match = re.search(r'gene_(?:bio)?type "([^"]+)"', attributes)
			gene_is_protein_coding[gene_id] = type_match is not None and type_match.group(1) == "protein_coding"
			feature_length = int(fields[4]) - int(fields[3]) + 1
			if feature == "CDS":
				cds_length[transcript_id] += feature_length
				cds_lines.setdefault(transcript_id, []).append(line)
			else:
				exon_length[transcript_id] += feature_length

	size_of = exon_length if mode == "longest_spliced" else cds_length
	best_by_gene = {}
	for transcript_id in transcript_order:
		if transcript_id not in cds_lines:
			continue
		gene_id = gene_of_transcript[transcript_id]
		if mode == "longest_cds_pc" and not gene_is_protein_coding[gene_id]:
			continue
		current = best_by_gene.get(gene_id)
		if current is None or size_of[transcript_id] > size_of[current]:
			best_by_gene[gene_id] = transcript_id

	chosen = set(best_by_gene.values())
	written = 0
	with open(out_path, "w") as out:
		for transcript_id in transcript_order:
			if transcript_id in chosen:
				for line in cds_lines[transcript_id]:
					out.write(line)
					written += 1
	print(mode, in_path.split("/")[-1], "genes", len(best_by_gene), "CDS lines", written)


if __name__ == "__main__":
	main()
