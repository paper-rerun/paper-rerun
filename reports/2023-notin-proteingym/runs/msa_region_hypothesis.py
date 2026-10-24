"""Diagnostic, chosen after seeing data: the 5 assays that disagree with the authors' ESM2 scores are exactly the 5
long assays whose MSA covers only part of target_seq. Test whether the authors scored only the MSA region
(target_seq[MSA_start-1:MSA_end], mutant offset MSA_start), as compute_fitness.py does for MSA Transformer.
Usage: msa_region_hypothesis.py <checkpoint> <our column> <authors column> <DMS index> [...]
"""
import sys
import pandas as pd
import torch
from scipy.stats import spearmanr

REPO = "/mnt/e/Ciencia/meio/2023-notin-proteingym/repo"
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
sys.path.insert(0, REPO + "/proteingym/baselines/esm")
sys.path.insert(0, REPO + "/proteingym")
sys.path.insert(0, REPO)
import compute_fitness

Checkpoint, AuthorsColumn = sys.argv[1], sys.argv[2]
Model, Alphabet = compute_fitness.pretrained.load_model_and_alphabet(Checkpoint)
Model = Model.eval().cuda()
Reference = pd.read_csv(REPO + "/reference_files/DMS_substitutions.csv")

for DmsIndex in [int(X) for X in sys.argv[3:]]:
	Row = Reference.iloc[DmsIndex]
	MsaStart = int(Row["MSA_start"])
	MsaEnd = int(Row["MSA_end"])
	# Only the MSA-covered region, the mutant positions then count from MSA_start
	Region = Row["target_seq"].upper()[MsaStart - 1:MsaEnd]
	Dms = pd.read_csv(f"{W}/data/dms/DMS_ProteinGym_substitutions/{Row['DMS_filename']}")
	Authors = pd.read_csv(f"{W}/sources/authors_esm_scores/{Row['DMS_id']}.csv").set_index("mutant")[AuthorsColumn]
	_, _, Tokens = Alphabet.get_batch_converter()([("protein1", Region)])
	AllProbs = []
	for Position in range(Tokens.size(1)):
		Masked = Tokens.clone()
		Masked[0, Position] = Alphabet.mask_idx
		with torch.no_grad():
			Probs = torch.log_softmax(Model(Masked.cuda())["logits"], dim=-1)
		AllProbs.append(Probs[:, Position].cpu())
	TokenProbs = torch.cat(AllProbs, dim=0).unsqueeze(0)
	Scores = Dms["mutant"].apply(lambda Mutant: compute_fitness.label_row(Mutant, Region, TokenProbs, Alphabet, MsaStart))
	AuthorsScores = Authors.reindex(Dms["mutant"]).values
	MaxDiff = float(abs(Scores.values - AuthorsScores).max())
	print(f"{AuthorsColumn} {Row['DMS_id']} region={MsaStart}-{MsaEnd} spearman_vs_authors={spearmanr(Scores, AuthorsScores)[0]:.6f} max_abs_diff={MaxDiff:.2e} spearman_vs_DMS={spearmanr(Scores, Dms['DMS_score'])[0]:.3f}", flush=True)
