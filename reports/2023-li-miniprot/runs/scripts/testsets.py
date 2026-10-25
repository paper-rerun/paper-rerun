# Build the query protein sets: the pre-registered main sets (TS-ZF, TS-MM, TS-AG)
# and the variants listed under alternative_readings in claims.json.
# Usage: python3 -I testsets.py <data_dir> <out_dir>
import gzip
import re
import sys
import os


def read_fasta(path):
	# Yield (header_without_gt, sequence) in file order
	header = None
	chunks = []
	with gzip.open(path, "rt") as handle:
		for line in handle:
			line = line.rstrip("\n")
			if line.startswith(">"):
				if header is not None:
					yield header, "".join(chunks)
				header = line[1:]
				chunks = []
			else:
				chunks.append(line)
	if header is not None:
		yield header, "".join(chunks)


def pick_longest_per_gene(records, gene_of):
	# records: list of (index, header, seq); gene_of: header -> gene id or None (drop)
	# Longest aa length wins, ties go to the first record in file order
	best_by_gene = {}
	for index, header, seq in records:
		gene_id = gene_of(header)
		if gene_id is None:
			continue
		current = best_by_gene.get(gene_id)
		if current is None or len(seq) > len(current[2]):
			best_by_gene[gene_id] = (index, header, seq)
	return sorted(best_by_gene.values())


def write_fasta(path, picked, name_of):
	names_seen = set()
	with open(path, "w") as out:
		for index, header, seq in picked:
			name = name_of(header)
			if name in names_seen:
				raise SystemExit("duplicate name " + name + " in " + path)
			names_seen.add(name)
			out.write(">" + name + "\n")
			for start in range(0, len(seq), 60):
				out.write(seq[start:start + 60] + "\n")
	print(os.path.basename(path), len(picked))


def ensembl_field(header, key):
	match = re.search(r"(?:^| )" + key + r":(\S+)", header)
	return match.group(1) if match else None


def first_token(header):
	return header.split()[0]


def main():
	data_dir = sys.argv[1]
	out_dir = sys.argv[2]
	os.makedirs(out_dir + "/alt", exist_ok=True)

	# Zebrafish, Ensembl 107 pep.all
	zf_records = [(i, h, s) for i, (h, s) in enumerate(read_fasta(data_dir + "/zebrafish/Danio_rerio.GRCz11.pep.all.fa.gz"))]
	primary_chromosomes = set(str(n) for n in range(1, 26))

	def location_parts(header):
		# e.g. "chromosome:GRCz11:20:33294428:33302175:1" -> ("chromosome", "20")
		tokens = header.split()
		parts = tokens[2].split(":")
		return parts[0], parts[2]

	def zf_main(header):
		coord_system, seq_region = location_parts(header)
		if ensembl_field(header, "gene_biotype") != "protein_coding":
			return None
		if coord_system != "chromosome" or seq_region not in primary_chromosomes:
			return None
		return ensembl_field(header, "gene")

	def any_gene(header):
		return ensembl_field(header, "gene")

	def zf_plus_mt(header):
		coord_system, seq_region = location_parts(header)
		if ensembl_field(header, "gene_biotype") != "protein_coding":
			return None
		if coord_system != "chromosome" or (seq_region not in primary_chromosomes and seq_region != "MT"):
			return None
		return ensembl_field(header, "gene")

	def zf_no_alt(header):
		coord_system, seq_region = location_parts(header)
		if ensembl_field(header, "gene_biotype") != "protein_coding":
			return None
		if seq_region.startswith("CHR_ALT") or "ALT" in seq_region:
			return None
		return ensembl_field(header, "gene")

	def zf_main_pc_transcript(header):
		if ensembl_field(header, "transcript_biotype") != "protein_coding":
			return None
		return zf_main(header)

	write_fasta(out_dir + "/zebrafish.longest.faa", pick_longest_per_gene(zf_records, zf_main), first_token)
	write_fasta(out_dir + "/alt/zf_A_all.faa", pick_longest_per_gene(zf_records, any_gene), first_token)
	write_fasta(out_dir + "/alt/zf_B1_plusMT.faa", pick_longest_per_gene(zf_records, zf_plus_mt), first_token)
	write_fasta(out_dir + "/alt/zf_B2_noALT_allregions.faa", pick_longest_per_gene(zf_records, zf_no_alt), first_token)
	write_fasta(out_dir + "/alt/zf_C_pctranscript.faa", pick_longest_per_gene(zf_records, zf_main_pc_transcript), first_token)

	# Location census, so the report can say what the regions look like
	census = {}
	for index, header, seq in zf_records:
		coord_system, seq_region = location_parts(header)
		key = coord_system + ":" + ("1-25" if seq_region in primary_chromosomes else ("MT" if seq_region == "MT" else ("ALT" if "ALT" in seq_region else "other")))
		census[key] = census.get(key, 0) + 1
	print("zebrafish location census (records):", census)

	# Mosquito, Ensembl Metazoa 54 pep.all, all records
	ag_records = [(i, h, s) for i, (h, s) in enumerate(read_fasta(data_dir + "/mosquito/Anopheles_gambiae.AgamP4.pep.all.fa.gz"))]
	write_fasta(out_dir + "/mosquito.longest.faa", pick_longest_per_gene(ag_records, any_gene), first_token)

	# Mouse, Gencode M30
	canonical_transcripts = set()
	gene_type_by_gene = {}
	genes_with_cds = set()
	with gzip.open(data_dir + "/mouse/gencode.vM30.annotation.gtf.gz", "rt") as handle:
		for line in handle:
			if line.startswith("#"):
				continue
			fields = line.rstrip("\n").split("\t")
			attributes = fields[8]
			gene_id = re.search(r'gene_id "([^"]+)"', attributes).group(1)
			if fields[2] == "gene":
				gene_type_by_gene[gene_id] = re.search(r'gene_type "([^"]+)"', attributes).group(1)
			elif fields[2] == "transcript":
				if 'tag "Ensembl_canonical"' in attributes:
					canonical_transcripts.add(re.search(r'transcript_id "([^"]+)"', attributes).group(1))
			elif fields[2] == "CDS":
				genes_with_cds.add(gene_id)
	print("mouse canonical transcripts in GTF:", len(canonical_transcripts))

	mm_records = [(i, h, s) for i, (h, s) in enumerate(read_fasta(data_dir + "/mouse/gencode.vM30.pc_translations.fa.gz"))]

	def mm_name(header):
		return header.split("|")[0]

	def mm_canonical(header):
		# Each canonical transcript is its own group, so every match is kept
		transcript_id = header.split("|")[1]
		return transcript_id if transcript_id in canonical_transcripts else None

	def mm_canonical_pc(header):
		parts = header.split("|")
		if gene_type_by_gene.get(parts[2]) != "protein_coding":
			return None
		return mm_canonical(header)

	def mm_longest_pc_gene(header):
		gene_id = header.split("|")[2]
		if gene_type_by_gene.get(gene_id) != "protein_coding" or gene_id not in genes_with_cds:
			return None
		return gene_id

	write_fasta(out_dir + "/mouse.testset.faa", pick_longest_per_gene(mm_records, mm_canonical), mm_name)
	write_fasta(out_dir + "/alt/mm_A_longest_pc.faa", pick_longest_per_gene(mm_records, mm_longest_pc_gene), mm_name)
	write_fasta(out_dir + "/alt/mm_B_canonical_pc.faa", pick_longest_per_gene(mm_records, mm_canonical_pc), mm_name)


if __name__ == "__main__":
	main()
