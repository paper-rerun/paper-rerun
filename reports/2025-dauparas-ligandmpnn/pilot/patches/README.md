# Patches

None. `repo/` is the authors' clone at 26ec57a with nothing changed in it - the only
untracked thing is `model_params/`, which `get_model_params.sh` puts there by design.
`git status --porcelain` inside `repo/` prints just that one line.

Everything we added lives one level up, as scripts that call the authors' `run.py`:

- `../setup_env.sh` - builds the venv from the authors' own `requirements.txt`
- `../fetch_pdbs.sh` - downloads biological assembly 1 for each test id
- `../run_benchmark.py` - drives `run.py` over the test splits, saves per-design stats
- `../score_recovery.py` - near-ligand sequence recovery from those stats
- `../run_all.sh`, `../status.sh`, `../check_pdbs.sh` - run and watch

One environment fix was needed and it is outside the repo too: `requirements.txt` does not
pin setuptools, and ProDy 2.4.1 imports `pkg_resources`, which setuptools 81 removed. The
fresh install picked setuptools 84.2.1 and ProDy would not import. Fixed by installing
`setuptools<81` into the venv. No code change, and `env/requirements-lock.txt` records it.
