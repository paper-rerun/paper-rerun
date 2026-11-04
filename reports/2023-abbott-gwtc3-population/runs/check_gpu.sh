#!/bin/bash
nvidia-smi; ls /usr/lib/wsl/lib | head -30; free -g; nproc; ~/.local/bin/uv --version; ~/.local/bin/uv python list 2>/dev/null | head -30
