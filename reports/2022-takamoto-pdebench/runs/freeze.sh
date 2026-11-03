cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
VIRTUAL_ENV=env/.venv ~/.local/bin/uv pip freeze > env/freeze.txt; env/.venv/bin/python -V >> env/freeze.txt; uname -r >> env/freeze.txt; head -40 env/freeze.txt
