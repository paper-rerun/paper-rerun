"""Tests whether the invalid SMILES are truncated sequences, and whether max_len explains it.

Every invalid sequence we looked at by hand ends in unbalanced brackets, which is what a
sequence cut before its EOS looks like. VocSmiles.fromFile defaults to max_len=100, and
nothing in the release says which max_len produced Table S4. If validity climbs with
max_len, then the printed 0.999 and 1.000 are a sampling setting and not a property of the
model.

Samples the same model at several max_len values and reports validity for each, plus how
many invalid sequences used every token available.

Usage: 04_truncation.py <pkg> <vocab> lstm|gru <n> <batch> <out.json>
"""
import json
import os
import sys

import torch
from rdkit import Chem, RDLogger

from drugex.data.corpus.vocabulary import VocSmiles
from drugex.training.generators import SequenceRNN

RDLogger.DisableLog("rdApp.*")

PKG, VOCAB, KIND, N, BATCH, OUT = (sys.argv[1], sys.argv[2], sys.argv[3],
	int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
torch.set_num_threads(int(os.environ.get("DRUGEX_THREADS", "2")))

out = {}
for max_len in (100, 120, 140, 200):
	voc = VocSmiles.fromFile(VOCAB, False, max_len=max_len)
	model = SequenceRNN(voc, is_lstm=(KIND == "lstm"), use_gpus=(-1,))
	model.loadStatesFromFile(PKG)
	model.eval()

	sampled = []
	with torch.no_grad():
		while len(sampled) < N:
			sampled.extend(model.sample(BATCH))
	sampled = sampled[:N]

	valid = 0
	invalid_at_token_limit = 0
	for smi in sampled:
		if Chem.MolFromSmiles(smi) is not None:
			valid += 1
			continue
		# A sequence that used every token it was given was cut off, not finished
		if len(voc.splitSequence(smi)) >= max_len - 1:
			invalid_at_token_limit += 1
	out["max_len_%d" % max_len] = {
		"n": N,
		"validity": valid / N,
		"invalid": N - valid,
		"invalid_at_token_limit": invalid_at_token_limit,
	}
	print(max_len, json.dumps(out["max_len_%d" % max_len]), flush=True)

open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1))
