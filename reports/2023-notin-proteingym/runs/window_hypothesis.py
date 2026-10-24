"""Diagnostic, chosen after seeing data: why do 5 long-protein assays disagree with the authors' ESM2 scores?

For one assay, score masked-marginals three ways and compare each with the authors' per-mutant scores:
  optimal  - the repo's get_optimal_window (what compute_fitness.py does, our main run)
  full     - whole sequence in one pass, no window (ESM2 has rotary positions, so it runs past 1024)
  window1022 - optimal window logic but with model_window=1022 (ESM-1b style limit)
Usage: window_hypothesis.py <checkpoint> <authors column> <DMS index> [<DMS index> ...]
"""
import sys
import pandas as pd
import torch
from scipy.stats import spearmanr

REPO = "/mnt/e/Ciencia/meio/2023-notin-proteingym/repo"
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
sys.path.insert(0, REPO + "/proteingym/baselines/esm")
sys.path.insert(0, REPO + "/proteingym")
import compute_fitness
from utils.scoring_utils import get_optimal_window

Checkpoint, AuthorsColumn = sys.argv[1], sys.argv[2]
Model, Alphabet = compute_fitness.pretrained.load_model_and_alphabet(Checkpoint)
Model = Model.eval().cuda()
Reference = pd.read_csv(REPO + "/reference_files/DMS_substitutions.csv")


def MaskedMarginals(Tokens, Mode):
	AllProbs = []
	Length = Tokens.size(1)
	for Position in range(Length):
		Masked = Tokens.clone()
		Masked[0, Position] = Alphabet.mask_idx
		Start = 0
		if Mode == "optimal" and Length > 1024:
			Start, End = get_optimal_window(mutation_position_relative=Position, seq_len_wo_special=Length, model_window=1024)
			Masked = Masked[:, Start:End]
		elif Mode == "window1022" and Length > 1022:
			Start, End = get_optimal_window(mutation_position_relative=Position, seq_len_wo_special=Length, model_window=1022)
			Masked = Masked[:, Start:End]
		with torch.no_grad():
			Probs = torch.log_softmax(Model(Masked.cuda())["logits"], dim=-1)
		AllProbs.append(Probs[:, Position - Start].cpu())
	return torch.cat(AllProbs, dim=0).unsqueeze(0)


for DmsIndex in [int(X) for X in sys.argv[3:]]:
	Row = Reference.iloc[DmsIndex]
	Sequence = Row["target_seq"].upper()
	Dms = pd.read_csv(f"{W}/data/dms/DMS_ProteinGym_substitutions/{Row['DMS_filename']}")
	Authors = pd.read_csv(f"{W}/sources/authors_esm_scores/{Row['DMS_id']}.csv").set_index("mutant")[AuthorsColumn]
	_, _, Tokens = Alphabet.get_batch_converter()([("protein1", Sequence)])
	for Mode in ["optimal", "full", "window1022"]:
		TokenProbs = MaskedMarginals(Tokens, Mode)
		Scores = Dms["mutant"].apply(lambda Mutant: compute_fitness.label_row(Mutant, Sequence, TokenProbs, Alphabet, 1))
		Agreement = spearmanr(Scores, Authors.reindex(Dms["mutant"]).values)[0]
		VsDms = spearmanr(Scores, Dms["DMS_score"])[0]
		print(f"{Row['DMS_id']} len={len(Sequence)} mode={Mode:10s} spearman_vs_authors={Agreement:.6f} spearman_vs_DMS={VsDms:.3f}", flush=True)
	print(f"{Row['DMS_id']} authors spearman_vs_DMS={spearmanr(Authors.reindex(Dms['mutant']).values, Dms['DMS_score'])[0]:.3f}", flush=True)
