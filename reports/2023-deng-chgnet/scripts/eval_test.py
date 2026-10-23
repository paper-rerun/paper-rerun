"""Evaluate a pretrained CHGNet on the MPtrj test JSONL written by make_test_split.py.

MAEs are computed with the authors' own CombinedLoss (chgnet/trainer/trainer.py), the same
code Trainer._validate uses for the test numbers. Each batch MAE is weighted by the size the
loss reports, so the result is the mean over all structures (energy), all force components,
all stress components and all labelled magmoms, exactly like the authors' AverageMeter.

Label transforms copy StructureData.__getitem__: stress * -0.1 (VASP kBar -> GPa, sign
flipped), |magmom|, missing magmom -> None.

Usage: python eval_test.py <test.jsonl> <model_name> <out_prefix> [max_frames] [batch_size] [device]
max_frames > 0 evaluates a random subset (first max_frames frames after the seeded shuffle).
device=cpu runs with no loader workers so the job stays at 4 threads.
"""

import json
import os
import random
import sys
import time

import torch
from pymatgen.core import Structure
from torch.utils.data import DataLoader, Dataset

from chgnet.data.dataset import collate_graphs
from chgnet.model import CHGNet
from chgnet.trainer.trainer import CombinedLoss

TORCH_DTYPE = torch.float32


class JsonlStructureData(Dataset):
	"""Frames from the test JSONL, converted to graphs with the model's own converter"""

	def __init__(self, rows, graph_converter):
		self.rows = rows
		self.graph_converter = graph_converter

	def __len__(self):
		return len(self.rows)

	def __getitem__(self, idx):
		# Rows stay as raw lines until here, so the 4 forked workers share them without copying
		row = json.loads(self.rows[idx])
		try:
			structure = Structure.from_dict(row["structure"])
			crystal_graph = self.graph_converter(structure, graph_id=row["frame_id"], mp_id=row["mp_id"])
		except Exception as error:
			# Same as training: frames that can't become a graph (isolated atoms) are left out
			return {"failed": row["frame_id"], "error": repr(error)}
		targets = {
			"e": torch.tensor(row["energy_per_atom"], dtype=TORCH_DTYPE),
			"f": torch.tensor(row["force"], dtype=TORCH_DTYPE),
			"s": torch.tensor(row["stress"], dtype=TORCH_DTYPE) * (-0.1),
		}
		if row["magmom"] is None:
			targets["m"] = None
		else:
			targets["m"] = torch.abs(torch.tensor(row["magmom"], dtype=TORCH_DTYPE))
		return crystal_graph, targets


def collate_skip_failed(batch_data):
	failed = [item for item in batch_data if isinstance(item, dict)]
	good = [item for item in batch_data if not isinstance(item, dict)]
	if not good:
		return None, None, failed
	graphs, targets = collate_graphs(good)
	return graphs, targets, failed


def main():
	jsonl_path = sys.argv[1]
	model_name = sys.argv[2]
	out_prefix = sys.argv[3]
	max_frames = int(sys.argv[4]) if len(sys.argv) > 4 and int(sys.argv[4]) > 0 else None
	batch_size = int(sys.argv[5]) if len(sys.argv) > 5 else 40
	device = sys.argv[6] if len(sys.argv) > 6 else "cuda"
	torch.set_num_threads(4)
	# Each graph carries many small tensors; the default fd sharing runs out of file handles
	torch.multiprocessing.set_sharing_strategy("file_system")

	model = CHGNet.load(model_name=model_name, use_device=device)
	model.eval()
	criterion = CombinedLoss(target_str="efsm", criterion="Huber", delta=0.1, allow_missing_labels=True)

	rows = []
	with open(jsonl_path) as jsonl_file:
		for line in jsonl_file:
			rows.append(line)
	# Shuffle frames (fixed seed) so the running MAE is an unbiased estimate if the run is cut short,
	# and so max_frames takes a random subset instead of the first materials in file order
	random.Random(0).shuffle(rows)
	if max_frames is not None:
		rows = rows[:max_frames]
	# EVAL_SKIP drops frames another run already covered, so two runs add up to one disjoint sample
	rows = rows[int(os.environ.get("EVAL_SKIP", "0")):]
	print(f"{len(rows)} frames", flush=True)

	dataset = JsonlStructureData(rows, model.graph_converter)
	loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=4 if device == "cuda" else 0, collate_fn=collate_skip_failed)

	# Running sums of MAE * size, per target, like the authors' AverageMeter
	weighted_sums = {key: 0.0 for key in "efsm"}
	sizes = {key: 0 for key in "efsm"}
	failed_frames = []
	per_frame_rows = []
	start_time = time.time()
	# Optional wall-clock deadline (unix time) for the shared GPU: stop cleanly and save what we have
	deadline = float(os.environ.get("EVAL_DEADLINE", "inf"))
	for batch_index, (graphs, targets, failed) in enumerate(loader):
		if time.time() > deadline:
			print(f"deadline reached after {batch_index} batches, stopping early", flush=True)
			break
		failed_frames.extend(failed)
		if graphs is None:
			continue
		for graph in graphs:
			graph.atom_frac_coord.requires_grad = True
		graphs = [graph.to(device) for graph in graphs]
		targets_on_device = {}
		for key, value in targets.items():
			if key == "e":
				targets_on_device[key] = value.to(device)
			else:
				targets_on_device[key] = [None if each is None else each.to(device) for each in value]
		prediction = model(graphs, task="efsm")
		combined_loss = criterion(targets_on_device, prediction)
		for key in "efsm":
			weighted_sums[key] += combined_loss[f"{key}_MAE"].detach().cpu().item() * combined_loss[f"{key}_MAE_size"]
			sizes[key] += combined_loss[f"{key}_MAE_size"]

		# Keep the per-frame energy error so the split can be inspected later
		energy_errors = (prediction["e"].detach() - targets_on_device["e"]).abs().cpu().tolist()
		for graph, energy_error in zip(graphs, energy_errors):
			per_frame_rows.append((graph.mp_id, graph.graph_id, energy_error))

		if batch_index % 50 == 0:
			running = {key: weighted_sums[key] / max(sizes[key], 1) for key in "efsm"}
			print(f"batch {batch_index}, {len(per_frame_rows)} frames, {time.time() - start_time:.0f}s, running MAE e={running['e'] * 1000:.1f} meV/atom f={running['f'] * 1000:.1f} meV/A s={running['s']:.3f} GPa m={running['m']:.4f} muB", flush=True)

	result = {
		"model": model_name,
		"jsonl": jsonl_path,
		"n_frames_evaluated": len(per_frame_rows),
		"n_frames_failed_graph": len(failed_frames),
		"n_materials": len({row[0] for row in per_frame_rows}),
		"energy_MAE_meV_per_atom": weighted_sums["e"] / sizes["e"] * 1000,
		"force_MAE_meV_per_A": weighted_sums["f"] / sizes["f"] * 1000,
		"stress_MAE_GPa": weighted_sums["s"] / sizes["s"],
		"magmom_MAE_muB": weighted_sums["m"] / sizes["m"],
		"sizes": sizes,
		"wall_seconds": time.time() - start_time,
	}
	print(json.dumps(result, indent=1), flush=True)
	with open(f"{out_prefix}_result.json", "w") as result_file:
		json.dump({**result, "failed_frames": failed_frames}, result_file, indent=1)
	with open(f"{out_prefix}_energy_errors.csv", "w") as csv_file:
		csv_file.write("mp_id,frame_id,abs_energy_error_eV_per_atom\n")
		for mp_id, frame_id, energy_error in per_frame_rows:
			csv_file.write(f"{mp_id},{frame_id},{energy_error:.6f}\n")


if __name__ == "__main__":
	main()
