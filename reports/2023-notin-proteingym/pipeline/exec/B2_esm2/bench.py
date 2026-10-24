# Throughput benchmark on a synthetic sequence (no DMS data, no scores): time of one masked forward pass per size and length,
# same load path and fp32 as compute_fitness.py. Used only to size the GPU budget
import os, sys, time
Start = time.time()
import torch
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo/proteingym")
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo/proteingym/baselines/esm")
from baselines.esm import esm
from esm import pretrained
print("import s", round(time.time() - Start, 1), flush=True)
W = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/weights/"
for Name in sys.argv[1:]:
	LoadStart = time.time()
	Model, Alphabet = pretrained.load_model_and_alphabet(W + Name + ".pt")
	Model.eval().cuda()
	print(Name, "load s", round(time.time() - LoadStart, 1), flush=True)
	Converter = Alphabet.get_batch_converter()
	for Length in [100, 300, 600, 1022]:
		_, _, Tokens = Converter([("x", "ACDEFGHIKLMNPQRSTVWY" * (Length // 20) + "A" * (Length % 20))])
		with torch.no_grad():
			for Repeat in range(3):
				torch.log_softmax(Model(Tokens.cuda())["logits"], dim=-1)
			torch.cuda.synchronize()
			PassStart = time.time()
			for Repeat in range(20):
				torch.log_softmax(Model(Tokens.cuda())["logits"], dim=-1)
			torch.cuda.synchronize()
		print(Name, Length, "s/pass", round((time.time() - PassStart) / 20, 4), flush=True)
	del Model
	torch.cuda.empty_cache()
