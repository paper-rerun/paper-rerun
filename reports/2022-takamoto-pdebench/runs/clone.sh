cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
[ -d repo ] || git clone -q https://github.com/pdebench/PDEBench.git repo
cd repo && git checkout -q b5b646f12802c283265e4c850566e2a11503624a && git log -1 --format='%H %ad %s'
git log -1 --format='%H %s' 268ba5e
cat pyproject.toml 2>/dev/null | head -80; ls
