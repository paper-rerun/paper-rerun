# Environment

One venv per paper, built with `uv` from the authors' own `repo/requirements.txt`, no pins
changed. `setup_env.sh` at the folder root rebuilds it; `requirements-lock.txt` is what
actually got installed.

- Python 3.11 (the README's suggested version)
- torch 2.2.1 from the default PyPI wheel (CUDA 12.1), which covers the RTX 2070 SUPER (sm_75)
- WSL2 Ubuntu 24.04

No Dockerfile: `requirements.txt` pins exact versions already and installed clean, so a
container would have added nothing.

Note for anyone rebuilding on a Windows drive: the venv lives on `/mnt/e` (DrvFs), where uv
cannot hardlink from its cache and copies instead. The install is slow (minutes, ~3 GB) but
works.
