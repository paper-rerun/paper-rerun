#!/usr/bin/env bash
# Same two runs as run_block.sh, but restartable: each pass designs only the entries
# whose stats file is still missing, so a kill costs at most the entry in flight.
# The GPU lock is shared with the other blocks, so this can sit idle for a long time.
# Usage: resume.sh <flavor>
set -uo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
EXEC=$ROOT/exec/B3-metal-split
FLAVOR=${1:-biounit1}

source "$ROOT/env/activate.sh"

run_one () {        # $1 tag, $2 model_type, $3 checkpoint flag, $4 checkpoint, $5 seed
	local tag=$1 mtype=$2 ckflag=$3 ckpt=$4 seed=$5
	local out=$EXEC/out/${tag}_$FLAVOR
	local todo=$EXEC/todo_${tag}_$FLAVOR.json

	python - "$FLAVOR" "$out" "$todo" <<'PY'
import json, os, sys
flavor, out, todo = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
EXEC = ROOT + "/exec/B3-metal-split"
ids = json.load(open(ROOT + "/repo/training/test_metal.json"))
done = set()
if os.path.isdir(out + "/stats"):
    done = {f[:-3] for f in os.listdir(out + "/stats") if f.endswith(".pt")}
missing = [i for i in ids if i not in done]
paths = {}
for i in missing:
    p = "%s/fixed/%s/5l70.pdb" % (EXEC, flavor) if i == "5l70" \
        else "%s/data/structures/%s/%s.pdb" % (ROOT, flavor, i)
    paths[p] = ""
json.dump(paths, open(todo, "w"), indent=1)
print("%s: %d done, %d to design" % (out.rsplit("/", 1)[-1], len(done), len(missing)))
PY

	if [ "$(python -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$todo")" = "0" ]; then
		echo "nothing to do for $tag"
		return 0
	fi

	flock /mnt/e/Ciencia/.gpu.lock python run.py \
		--model_type "$mtype" "$ckflag" "$ckpt" \
		--pdb_path_multi "$todo" --out_folder "$out" \
		--batch_size 10 --number_of_batches 1 \
		--temperature 0.1 --seed "$seed" \
		--ligand_mpnn_use_atom_context 1 \
		--ligand_mpnn_use_side_chain_context 0 \
		--save_stats 1 --verbose 0
}

run_one lmpnn ligand_mpnn  --checkpoint_ligand_mpnn  "$ROOT/data/model_params/ligandmpnn_v_32_010_25.pt" 37
run_one pmpnn protein_mpnn --checkpoint_protein_mpnn "$ROOT/data/model_params/proteinmpnn_v_48_010.pt"  38

L=$(ls "$EXEC/out/lmpnn_$FLAVOR/stats" 2>/dev/null | wc -l)
P=$(ls "$EXEC/out/pmpnn_$FLAVOR/stats" 2>/dev/null | wc -l)
echo "counts lmpnn=$L pmpnn=$P"
if [ "$L" = "83" ] && [ "$P" = "83" ]; then echo "DONE $FLAVOR"; fi
