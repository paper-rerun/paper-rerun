#!/bin/bash
# Blind-verification stage: build the environment again from nothing.
# Adapted from env/setup.sh and tools/01,03,05,08. Differences from the original:
#   - everything lands under verify/ (own clone, own venv), so the exec stage is untouched
#   - weights and structures are reused from data/, as the task allows (they are
#     downloads, not results)
#   - the structure download and the 5l70 conversion are skipped for the same reason
set -euo pipefail

ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
VROOT=$ROOT/verify
UV=$HOME/.local/bin/uv
COMMIT=26ec57ac976ade5379920dbd43c7f97a91cf82de

mkdir -p "$VROOT"/{repo,logs,out,tools}

# 1. The authors' code, fresh clone at the same commit
if [ ! -d "$VROOT/repo/.git" ]; then
	git clone https://github.com/dauparas/LigandMPNN.git "$VROOT/repo"
fi
git -C "$VROOT/repo" checkout --quiet "$COMMIT"
git -C "$VROOT/repo" status --porcelain
git -C "$VROOT/repo" log -1 --format="clone at %H %ci"

# 2. Python 3.11 per the authors' README, packages straight from the lockfile
"$UV" venv --clear --python 3.11 "$VROOT/env"
VIRTUAL_ENV="$VROOT/env" "$UV" pip install -r "$ROOT/env/requirements.lock.txt"

cat > "$VROOT/env/activate.sh" <<'EOF'
VROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/verify
source "$VROOT/env/bin/activate"
export LIGANDMPNN_WEIGHTS=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/model_params
export MPLBACKEND=Agg
cd "$VROOT/repo"
EOF

"$VROOT/env/bin/python" -c "import torch, numpy, prody, Bio, scipy; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'numpy', numpy.__version__, 'prody', prody.__version__, 'biopython', Bio.__version__, 'scipy', scipy.__version__)"

echo "=== lockfile diff (installed vs locked) ==="
VIRTUAL_ENV="$VROOT/env" "$UV" pip freeze > "$VROOT/logs/installed.txt"
diff <(sort "$ROOT/env/requirements.lock.txt") <(sort "$VROOT/logs/installed.txt") && echo "identical to the lockfile"

# 3. Smoke test 1: the default protein_mpnn path (tools/05_smallest_example.sh)
source "$VROOT/env/activate.sh"
mkdir -p "$VROOT/logs/smoke_default"
flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--seed 111 \
	--pdb_path "./inputs/1BC8.pdb" \
	--checkpoint_protein_mpnn "$LIGANDMPNN_WEIGHTS/proteinmpnn_v_48_020.pt" \
	--out_folder "$VROOT/logs/smoke_default"
echo "--- smoke_default fasta ---"
cat "$VROOT/logs/smoke_default"/seqs/*.fa

# 4. Smoke test 2: the ligand_mpnn path the claims use (tools/08_ligand_mpnn_smoke.sh)
mkdir -p "$VROOT/logs/smoke_ligand_mpnn"
flock /mnt/e/Ciencia/.gpu.lock python run.py \
	--model_type "ligand_mpnn" \
	--seed 111 \
	--pdb_path "./inputs/1BC8.pdb" \
	--checkpoint_ligand_mpnn "$LIGANDMPNN_WEIGHTS/ligandmpnn_v_32_010_25.pt" \
	--ligand_mpnn_use_atom_context 1 \
	--ligand_mpnn_use_side_chain_context 0 \
	--temperature 0.1 \
	--batch_size 2 \
	--number_of_batches 5 \
	--out_folder "$VROOT/logs/smoke_ligand_mpnn"
echo "--- smoke_ligand_mpnn fasta ---"
cat "$VROOT/logs/smoke_ligand_mpnn"/seqs/*.fa

echo "BUILD OK"
