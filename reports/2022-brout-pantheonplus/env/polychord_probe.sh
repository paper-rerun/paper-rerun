#!/bin/bash
# Record why the paper's sampler (PolyChord) was not used: what PyPI has, and whether it installs in our venv (dry run, nothing changes)
cd /mnt/e/Ciencia/noturno/2022-brout-pantheonplus
source env/activate.sh
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "python: $(python --version)"
echo "--- PyPI releases of pypolychord (pypi.org/pypi/pypolychord/json)"
curl -s https://pypi.org/pypi/pypolychord/json | python -c '
import json, sys
d = json.load(sys.stdin)
for v, files in d["releases"].items():
    for f in files:
        print(v, f["filename"], f["packagetype"], f["python_version"], f["upload_time"])
'
echo "--- uv pip install --dry-run pypolychord==1.15.1"
nice -n 19 ~/.local/bin/uv pip install --dry-run "pypolychord==1.15.1" 2>&1
echo "exit: $?"
echo "--- PolyChordLite from GitHub: not attempted (fetching and compiling it was not permitted in this session)"
