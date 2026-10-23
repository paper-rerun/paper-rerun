"""Stream MPtrj_2022.9_full.json and write a random 10% test split (by mp-id) as JSONL.

The authors split 8:1:1 by mp-id with an unseeded random.shuffle (chgnet/data/dataset.py,
GraphData.get_train_val_test_loader) and never published the ids, so the exact test set
can't be rebuilt. Here every mp-id goes to test with probability 0.1 (seeded), which is the
same procedure in distribution. The file is too big to json.load, so we stream it with ijson.

Usage: python make_test_split.py <MPtrj_2022.9_full.json> <out_dir> [seed] [expected_size_bytes]
With expected_size the parse can start while curl is still downloading the file.
"""

import json
import random
import sys
import time

import ijson

KEEP_KEYS = ["structure", "energy_per_atom", "corrected_total_energy", "force", "stress", "magmom"]
TEST_FRACTION = 0.1


class GrowingFile:
	"""Read a file that is still downloading: wait at EOF until it reaches the expected size"""

	def __init__(self, path, expected_size):
		self.file = open(path, "rb")
		self.expected_size = expected_size

	def read(self, size=-1):
		while True:
			data = self.file.read(size)
			# ijson probes with read(0) to detect bytes vs str, so an empty read on purpose returns right away
			if data or size == 0 or self.file.tell() >= self.expected_size:
				return data
			time.sleep(5)

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.file.close()


def main():
	json_path = sys.argv[1]
	out_dir = sys.argv[2]
	seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
	expected_size = int(sys.argv[4]) if len(sys.argv) > 4 else 0
	rng = random.Random(seed)

	print("ijson backend:", ijson.backend, flush=True)
	n_materials = 0
	n_frames = 0
	test_ids = []
	n_test_frames = 0
	start_time = time.time()
	with GrowingFile(json_path, expected_size) as json_file, open(f"{out_dir}/mptrj_test_seed{seed}.jsonl", "w") as out_file:
		for mp_id, frames in ijson.kvitems(json_file, "", use_float=True):
			n_materials += 1
			n_frames += len(frames)
			# One draw per material, in file order, so the split is fixed by the seed
			if rng.random() >= TEST_FRACTION:
				continue
			test_ids.append(mp_id)
			for frame_id, frame in frames.items():
				row = {"mp_id": mp_id, "frame_id": frame_id}
				for key in KEEP_KEYS:
					row[key] = frame.get(key)
				out_file.write(json.dumps(row) + "\n")
				n_test_frames += 1
			if n_materials % 10000 == 0:
				print(f"{n_materials} materials, {n_frames} frames, {len(test_ids)} test materials, {n_test_frames} test frames, {time.time() - start_time:.0f}s", flush=True)

	summary = {
		"seed": seed,
		"n_materials": n_materials,
		"n_frames": n_frames,
		"n_test_materials": len(test_ids),
		"n_test_frames": n_test_frames,
		"test_mp_ids": test_ids,
	}
	with open(f"{out_dir}/mptrj_test_seed{seed}_ids.json", "w") as ids_file:
		json.dump(summary, ids_file)
	print({k: v for k, v in summary.items() if k != "test_mp_ids"}, f"{time.time() - start_time:.0f}s", flush=True)


if __name__ == "__main__":
	main()
