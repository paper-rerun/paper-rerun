"""Samples one pretrained DrugEx RNN and measures validity and uniqueness as frozen.

Why this drives sample() in a loop instead of calling the authors' generate(): generate()
defaults to drop_invalid and drop_duplicates and keeps sampling until it holds num_samples
molecules, so its output is all valid and all unique by construction and the two ratios
cannot be computed from it. Table S4 reports ratios, so the table was made from a raw
sample. The loop below is the body of their generate() with the two filters off, calling
their SequenceRNN.sample() and their vocabulary decode, unmodified.

The metric is the one frozen in claims.json: validity over the sequences sampled, and
uniqueness over the valid ones, on canonical SMILES. Three secondary readings come out of
the same pass and go in the report without bearing on the verdict.

Usage: 03_sample.py <pkg> <vocab> lstm|gru <n> <batch> <out.json> <smiles.txt.gz>
"""
import gzip
import json
import os
import sys
import time

import torch
from rdkit import Chem, RDLogger

from drugex.data.corpus.vocabulary import VocSmiles
from drugex.training.generators import SequenceRNN

RDLogger.DisableLog("rdApp.*")


def peak_working_set_mb():
	"""Peak memory of this process, so the batch is never launched blind.

	A nightly run ate the 64 GB of this machine in 2026-11-16 because nobody read the
	pilot's peak. On Windows that number comes from GetProcessMemoryInfo.
	"""
	import ctypes
	import ctypes.wintypes

	class COUNTERS(ctypes.Structure):
		_fields_ = [("cb", ctypes.wintypes.DWORD),
			("PageFaultCount", ctypes.wintypes.DWORD),
			("PeakWorkingSetSize", ctypes.c_size_t),
			("WorkingSetSize", ctypes.c_size_t),
			("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
			("QuotaPagedPoolUsage", ctypes.c_size_t),
			("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
			("QuotaNonPagedPoolUsage", ctypes.c_size_t),
			("PagefileUsage", ctypes.c_size_t),
			("PeakPagefileUsage", ctypes.c_size_t)]

	counters = COUNTERS()
	counters.cb = ctypes.sizeof(counters)
	ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
	handle = ctypes.windll.kernel32.GetCurrentProcess()
	# Same function under two names; kernel32 carries it on current Windows
	for dll in (ctypes.windll.kernel32, ctypes.windll.psapi):
		fn = getattr(dll, "K32GetProcessMemoryInfo", None) or getattr(dll, "GetProcessMemoryInfo", None)
		if fn and fn(ctypes.c_void_p(handle), ctypes.byref(counters), ctypes.wintypes.DWORD(counters.cb)):
			break
	else:
		return None
	return round(counters.PeakWorkingSetSize / 1048576, 1)


PKG, VOCAB, KIND, N, BATCH, OUT, SMILES_OUT = (sys.argv[1], sys.argv[2], sys.argv[3],
	int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7])

# One thread per physical core at most, and the GPU is never touched: use_gpus=(-1,) is the
# flag the dev branch reads as CPU
torch.set_num_threads(int(os.environ.get("DRUGEX_THREADS", "6")))

voc = VocSmiles.fromFile(VOCAB, False)
model = SequenceRNN(voc, is_lstm=(KIND == "lstm"), use_gpus=(-1,))
model.loadStatesFromFile(PKG)
model.eval()

sampled = []
t0 = time.time()
with torch.no_grad():
	while len(sampled) < N:
		sampled.extend(model.sample(BATCH))
		if len(sampled) % (BATCH * 20) == 0:
			print("%d/%d  %.0fs" % (len(sampled), N, time.time() - t0), flush=True)
# A batch overshoots the target; the claim is n = 100000 exactly
sampled = sampled[:N]
sample_seconds = time.time() - t0

valid_canon = []
raw_distinct = set()
multifragment = 0
for smi in sampled:
	mol = Chem.MolFromSmiles(smi)
	raw_distinct.add(smi)
	if mol is None:
		continue
	canon = Chem.MolToSmiles(mol)
	if "." in canon:
		multifragment += 1
		continue
	valid_canon.append(canon)

n_valid = len(valid_canon)
distinct_valid = len(set(valid_canon))
result = {
	"model": os.path.basename(PKG),
	"kind": KIND,
	"n": N,
	"batch": BATCH,
	"sample_seconds": round(sample_seconds, 1),
	"ms_per_molecule": round(1000 * sample_seconds / N, 3),
	"frozen_validity": n_valid / N,
	"frozen_uniqueness": distinct_valid / n_valid if n_valid else None,
	"secondary_uniqueness_distinct_raw_over_n": len(raw_distinct) / N,
	"secondary_uniqueness_distinct_canonical_over_n": distinct_valid / N,
	"secondary_validity_parseable_including_multifragment": (n_valid + multifragment) / N,
	"n_valid": n_valid,
	"distinct_valid": distinct_valid,
	"multifragment": multifragment,
	"torch": torch.__version__,
	"rdkit": Chem.rdBase.rdkitVersion,
	"peak_working_set_mb": peak_working_set_mb(),
}
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(result, indent=1))
with gzip.open(SMILES_OUT, "wt", encoding="utf-8", newline="\n") as fh:
	fh.write("\n".join(sampled))
print(json.dumps(result, indent=1))
