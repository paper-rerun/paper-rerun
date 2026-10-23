import json
import time
import sys

t0 = time.time()
import torch
import numpy as np
from prody import parsePDB, writePDB
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
from data_utils import parse_PDB, featurize
from model_utils import ProteinMPNN
print("import", round(time.time() - t0, 1))

PDB = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split/inputs/1a28_ASTR.pdb"
CKPT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params/ligandmpnn_v_32_010_25.pt"

t = time.time()
device = torch.device("cuda")
ck = torch.load(CKPT, map_location=device)
model = ProteinMPNN(node_features=128, edge_features=128, hidden_dim=128,
                    num_encoder_layers=3, num_decoder_layers=3,
                    k_neighbors=ck["num_edges"], device=device,
                    atom_context_num=ck["atom_context_num"],
                    model_type="ligand_mpnn",
                    ligand_mpnn_use_side_chain_context=0)
model.load_state_dict(ck["model_state_dict"])
model.to(device)
model.eval()
print("model load", round(time.time() - t, 1))

t = time.time()
pd, backbone, other_atoms, icodes, _ = parse_PDB(PDB, device=device, chains=[],
                                                 parse_all_atoms=False,
                                                 parse_atoms_with_zero_occupancy=False)
print("parse_PDB", round(time.time() - t, 2))

pd["chain_mask"] = torch.ones(pd["X"].shape[0], device=device, dtype=torch.int32)
pd["membrane_per_residue_labels"] = torch.zeros(pd["X"].shape[0], device=device, dtype=torch.int32)
t = time.time()
fd = featurize(pd, cutoff_for_score=8.0, use_atom_context=True,
               number_of_ligand_atoms=ck["atom_context_num"], model_type="ligand_mpnn")
print("featurize", round(time.time() - t, 2))

B = 10
fd["batch_size"] = B
for k, v in fd.items():
    if isinstance(v, torch.Tensor):
        fd[k] = torch.repeat_interleave(v, B, 0) if v.shape[0] == 1 else v
fd["temperature"] = 0.1
fd["bias"] = torch.zeros([B, fd["S"].shape[1], 21], device=device)
fd["symmetry_residues"] = [[]]
fd["symmetry_weights"] = [[]]
fd["randn"] = torch.randn([B, fd["S"].shape[1]], device=device)

torch.cuda.synchronize()
t = time.time()
with torch.no_grad():
    out = model.sample(fd)
torch.cuda.synchronize()
print("sample b=10", round(time.time() - t, 2))

t = time.time()
with torch.no_grad():
    out = model.sample(fd)
torch.cuda.synchronize()
print("sample b=10 again", round(time.time() - t, 2))

t = time.time()
for i in range(10):
    writePDB("/tmp/prof_%d.pdb" % i, backbone + other_atoms if other_atoms else backbone)
print("writePDB x10 (tmpfs)", round(time.time() - t, 2))

t = time.time()
for i in range(10):
    writePDB("/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split/smoke_lmpnn/prof_%d.pdb" % i,
             backbone + other_atoms if other_atoms else backbone)
print("writePDB x10 (/mnt/e)", round(time.time() - t, 2))
