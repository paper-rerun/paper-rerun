# Time per forward pass of each ESM2 size at a few lengths, to size the GPU budget
import sys, time
import torch
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[1] + "/../..")
from esm import pretrained

WeightsFolder = sys.argv[2]
for Name in ["esm2_t6_8M_UR50D", "esm2_t12_35M_UR50D", "esm2_t30_150M_UR50D", "esm2_t33_650M_UR50D"]:
	LoadStart = time.time()
	Model, Alphabet = pretrained.load_model_and_alphabet(f"{WeightsFolder}/{Name}.pt")
	Model = Model.eval().cuda()
	LoadSeconds = time.time() - LoadStart
	for Length in [100, 300, 600, 1024]:
		Tokens = torch.randint(4, 24, (1, Length))
		with torch.no_grad():
			for Repeat in range(3):
				Model(Tokens.cuda())["logits"].sum().item()
			torch.cuda.synchronize()
			Start = time.time()
			for Repeat in range(10):
				torch.log_softmax(Model(Tokens.cuda())["logits"], dim=-1)[:, 5].cpu()
			torch.cuda.synchronize()
		print(f"{Name} load {LoadSeconds:.1f}s len {Length} {1000 * (time.time() - Start) / 10:.1f} ms/forward", flush=True)
	del Model
	torch.cuda.empty_cache()
