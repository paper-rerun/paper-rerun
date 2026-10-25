# After the 2026-10-25 ~05:00 PC freeze: env still imports, freeze still matches the lock snapshot, existing npz files load
source /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/env_activate.sh
python -c "import sys,torch,dgl,matgl;print(sys.version.split()[0],torch.__version__,dgl.__version__,matgl.__version__,torch.cuda.is_available())"
~/.local/bin/uv pip freeze --python env/bin/python > /tmp/freeze_now.txt
diff <(grep -v '^-e' /tmp/freeze_now.txt) <(grep -v '^-e' pip_freeze_verify.txt) && echo "freeze unchanged"
diff <(grep -v '^-e' /mnt/e/Ciencia/pipeline/2025-ko-matgl/env/pip_freeze.txt) <(grep -v '^-e' pip_freeze_verify.txt) && echo "freeze matches env/pip_freeze.txt"
git -C repo rev-parse HEAD; git -C repo status --porcelain | head
python - <<'PY'
import numpy as np, glob
for F in sorted(glob.glob("preds/*/*.npz")):
	D = np.load(F)
	N = D["natoms"]
	print(F, len(N), "E_MAE meV/atom", np.mean(np.abs(D["e_pred"]-D["e_dft"])/N)*1000, "F_MAE", D["f_abs_sum"].sum()/(3*N.sum()), "f_pred rows", D["f_pred"].shape, N.sum())
PY
