#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
free -g; nproc; ~/.local/bin/uv --version; python3 --version
[ -d repo/weatherbench2 ] || git clone -q https://github.com/google-research/weatherbench2 repo/weatherbench2
cd repo/weatherbench2 && git checkout -q 156e5dc9eafc18b8f8b215abc3a36b6305c266b8 && git log -1 --format='%H %cd' && cat setup.py
ls; uptime
