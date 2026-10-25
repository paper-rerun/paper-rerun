# Peak GPU memory and time of one forward+force pass per model, on TrpCage (312 atoms) batches of 1 and 2 conformations
# Run after the SO3Net 'device not ready' crash, to pick a batch size that stays well under 8 GB
import sys
import time

import torch
from ase import Atoms

import matgl
from matgl.ext.ase import Atoms2Graph

from predict import DataDir, ReadAllConformations, RunBatch, VerifyDir

ModelName = sys.argv[1]
Device = "cuda"
Potential = matgl.load_model(f"{VerifyDir}/repo/pretrained_models/{ModelName}-ANI-1x-Subset-PES").to(Device)
Potential.eval()
Converter = Atoms2Graph(Potential.model.element_types, Potential.model.cutoff)
Molecule = next(Item for Item in ReadAllConformations(f"{DataDir}/ANI-MD/ani_md_bench.h5") if "TrpCage" in Item["name"])
for BatchSize in [int(Value) for Value in sys.argv[2:]]:
	Graphs = []
	Lattices = []
	for ConfIndex in range(BatchSize):
		Graph, Lattice, _ = Converter.get_graph(Atoms(symbols=Molecule["species"], positions=Molecule["coordinates"][ConfIndex], pbc=False))
		Graphs.append(Graph)
		Lattices.append(Lattice)
	torch.cuda.reset_peak_memory_stats()
	StartTime = time.time()
	RunBatch(Potential, Graphs, Lattices, Device)
	torch.cuda.synchronize()
	print(ModelName, "atoms", BatchSize * len(Molecule["species"]), "edges", sum(Graph.num_edges() for Graph in Graphs), "peak MB", round(torch.cuda.max_memory_allocated() / 2**20), "s", round(time.time() - StartTime, 2), flush=True)
