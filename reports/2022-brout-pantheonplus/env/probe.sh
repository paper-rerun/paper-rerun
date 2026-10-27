#!/bin/bash
~/.local/bin/uv --version
~/.local/bin/uv python list 2>/dev/null | head -20
which gfortran gcc mpicc make cmake; gfortran --version | head -1
nproc; free -g | head -2; df -h /mnt/e | tail -1
uptime
