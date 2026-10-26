#!/bin/bash
H=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
$H/env/.venv/bin/python -I $H/runs/compare_perjet.py $H/runs/full_ParT_fp32 $H/runs/full_ParT_amp $H/runs/compare_ParT_fp32_vs_amp.json
