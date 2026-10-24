# Extra analysis, not the authors' pipeline: for one long assay where our scores differ from the authors' released ones,
# re-score with masked-marginals on the full target_seq (as the script does, optimal window) and on truncated prefixes of it,
# and see which input reproduces the authors' per-mutant scores. Only positions that carry a mutation are masked
# (masked marginal at i depends only on masking i, so this equals the full loop at those positions)
import sys, json
import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo/proteingym")
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo/proteingym/baselines/esm")
from baselines.esm import esm
from esm import pretrained
from utils.scoring_utils import get_optimal_window

W = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym"
Size, Checkpoint, DmsId = sys.argv[1], sys.argv[2], sys.argv[3]
Lengths = [int(Value) for Value in sys.argv[4:]]
Reference = pd.read_csv(f"{W}/repo/reference_files/DMS_substitutions.csv").set_index("DMS_id")
Sequence = Reference.loc[DmsId, "target_seq"]
Dms = pd.read_csv(f"{W}/data/DMS_ProteinGym_substitutions/{DmsId}.csv")
Authors = pd.read_csv(f"{W}/exec/B2_esm2/authors_merged/{DmsId}.csv", usecols=["mutant", f"ESM2_{Size}"])
Positions = sorted({int(Mutation[1:-1]) for Mutant in Dms.mutant for Mutation in Mutant.split(":")})
Model, Alphabet = pretrained.load_model_and_alphabet(f"{W}/data/weights/{Checkpoint}.pt")
Model.eval().cuda()
Converter = Alphabet.get_batch_converter()
Results = {}
for Length in [len(Sequence)] + Lengths:
	Prefix = Sequence[:Length]
	_, _, Tokens = Converter([("protein", Prefix)])
	LogProbs = {}
	for Position in Positions:
		# Token index of residue Position (1-based) is Position, because of BOS
		Masked = Tokens.clone()
		Masked[0, Position] = Alphabet.mask_idx
		Start = 0
		if Tokens.size(1) > 1024:
			Start, End = get_optimal_window(mutation_position_relative=Position, seq_len_wo_special=len(Prefix) + 2, model_window=1024)
			Masked = Masked[:, Start:End]
		with torch.no_grad():
			LogProbs[Position] = torch.log_softmax(Model(Masked.cuda())["logits"], dim=-1)[0, Position - Start].cpu()
	Scores = []
	for Mutant in Dms.mutant:
		Score = 0.0
		for Mutation in Mutant.split(":"):
			Wt, Position, Mt = Mutation[0], int(Mutation[1:-1]), Mutation[-1]
			Score += (LogProbs[Position][Alphabet.get_idx(Mt)] - LogProbs[Position][Alphabet.get_idx(Wt)]).item()
		Scores.append(Score)
	Frame = pd.DataFrame({"mutant": Dms.mutant, "score": Scores, "DMS_score": Dms.DMS_score}).merge(Authors, on="mutant")
	AbsDiff = (Frame.score - Frame[f"ESM2_{Size}"]).abs()
	Results[Length] = {"max_abs_diff_vs_authors": float(AbsDiff.max()), "mean_abs_diff_vs_authors": float(AbsDiff.mean()),
		"spearman_vs_DMS": float(spearmanr(Frame.DMS_score, Frame.score)[0]),
		"authors_spearman_vs_DMS": float(spearmanr(Frame.DMS_score, Frame[f"ESM2_{Size}"])[0])}
	print(Length, Results[Length], flush=True)
json.dump(Results, open(f"{W}/exec/B2_esm2/extra_truncation_{Size}_{DmsId}.json", "w"), indent=1)
