"""Load PlantCaduceus_l32 the way train_XGBoost.py does and time embedding extraction on 2048 train windows"""
import sys, time, logging
sys.path.insert(0, "/mnt/e/Ciencia/artigos/2025-zhai-plantcad/repo/src")
logging.basicConfig(level=logging.INFO)
import torch
from train_XGBoost import load_model_and_tokenizer, load_data, create_dataloader, extract_embeddings

Model, Tokenizer = load_model_and_tokenizer("kuleshov-group/PlantCaduceus_l32", "cuda:0")
import collections; print("params", Model.num_parameters(), "dtypes", collections.Counter(str(P.dtype) for P in Model.parameters()))
Sequences, Labels = load_data("/mnt/e/Ciencia/artigos/2025-zhai-plantcad/data/TIS/valid.tsv")
for BatchSize in (int(B) for B in sys.argv[1:] or ["64", "128"]):
	Loader = create_dataloader(Sequences[:2048], Tokenizer, BatchSize)
	torch.cuda.synchronize(); Start = time.time()
	Embeddings = extract_embeddings(Model, Loader, "cuda:0", 255)
	torch.cuda.synchronize(); Elapsed = time.time() - Start
	print(f"batch={BatchSize} shape={Embeddings.shape} seq/s={2048/Elapsed:.1f} peakGB={torch.cuda.max_memory_allocated()/1e9:.2f} nan={bool((Embeddings!=Embeddings).any())}")
