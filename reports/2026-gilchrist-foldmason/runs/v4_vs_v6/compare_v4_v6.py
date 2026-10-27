# Pull any v4 PDB of our 160 benchmark clusters' members out of the authors' afdb_scaling/pdbs.tar.gz
# and compare its ATOM records with the v6 file we saved under the v4 name
# Usage:
#   python3 -I compare_v4_v6.py scan <pdbs.tar.gz or /dev/stdin> <data/afdb_clusters> <out dir>
#   python3 -I compare_v4_v6.py compare - <data/afdb_clusters> <out dir>
import gzip
import os
import sys
import tarfile

MODE, TAR, DATA, OUT = sys.argv[1:5]
os.makedirs(OUT + "/v4", exist_ok=True)
FOUND_LIST = os.path.join(OUT, "found.tsv")

# All 3200 members (file name -> cluster) from the download list, including the ones the server no longer has
wanted = {}
cluster = None
for line in open(os.path.join(os.path.dirname(OUT.rstrip("/")), "afdb_download", "aria_list.txt")):
	if line.startswith("  dir="):
		cluster = os.path.basename(os.path.dirname(line.strip()[4:]))
	elif line.startswith("  out="):
		wanted[line.strip()[4:]] = cluster
print("names wanted", len(wanted), flush=True)

if MODE == "scan":
	found = {}
	scanned = 0
	with tarfile.open(TAR, "r|gz") as archive:
		for member in archive:
			scanned += 1
			base = os.path.basename(member.name)
			key = base[:-3] if base.endswith(".gz") else base
			# Members of the scaling tar are named by bare accession
			if not key.endswith(".pdb"):
				key = f"AF-{key}-F1-model_v4.pdb"
			if member.isfile() and key in wanted:
				data = archive.extractfile(member).read()
				if base.endswith(".gz"):
					data = gzip.decompress(data)
				with open(os.path.join(OUT, "v4", key), "wb") as handle:
					handle.write(data)
				found[key] = member.name
			if scanned % 10000 == 0:
				print("scanned", scanned, "found", len(found), flush=True)
	print("tar members scanned", scanned, "found", len(found), flush=True)
	with open(FOUND_LIST, "w") as handle:
		for key in sorted(found):
			handle.write(key + "\t" + found[key] + "\n")
	sys.exit(0)

# Compare mode
found = dict(row.rstrip("\n").split("\t") for row in open(FOUND_LIST))

def atoms(text):
	# Record name, atom, residue, chain, number and coordinates; B-factor (pLDDT) left out
	return [l[:54] for l in text.splitlines() if l.startswith("ATOM")]

def plddt(text):
	return [l[60:66] for l in text.splitlines() if l.startswith("ATOM")]

counts = {"same_coords": 0, "diff_coords": 0, "no_v6": 0}
with open(os.path.join(OUT, "v4_vs_v6.tsv"), "w") as report:
	report.write("file\tcluster\tv6_present\tsame_coords\tsame_plddt\tv4_atoms\tv6_atoms\n")
	for key in sorted(found):
		cluster = wanted[key]
		v4_text = open(os.path.join(OUT, "v4", key)).read()
		v6_path = os.path.join(DATA, cluster, "pdbs", key)
		if os.path.exists(v6_path):
			v6_text = open(v6_path).read()
			same = atoms(v4_text) == atoms(v6_text)
			counts["same_coords" if same else "diff_coords"] += 1
			report.write(f"{key}\t{cluster}\tyes\t{same}\t{plddt(v4_text) == plddt(v6_text)}\t{len(atoms(v4_text))}\t{len(atoms(v6_text))}\n")
		else:
			counts["no_v6"] += 1
			report.write(f"{key}\t{cluster}\tno\tNA\tNA\t{len(atoms(v4_text))}\t0\n")
print("v4 files found in the scaling tar:", len(found), counts)
