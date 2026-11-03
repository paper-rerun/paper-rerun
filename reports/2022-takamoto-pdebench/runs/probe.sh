cd /mnt/e/Ciencia/noturno/2022-takamoto-pdebench
which git curl python3 ~/.local/bin/uv; python3 --version; ~/.local/bin/uv --version; nproc; free -g
curl -s 'https://darus.uni-stuttgart.de/api/datasets/:persistentId/versions/1.0/files?persistentId=doi:10.18419/darus-2986' -o data/darus-2986_v1.0_files.json; ls -la data
curl -s 'https://darus.uni-stuttgart.de/api/datasets/:persistentId/versions/:latest/files?persistentId=doi:10.18419/darus-2987' -o data/darus-2987_latest_files.json; ls -la data
