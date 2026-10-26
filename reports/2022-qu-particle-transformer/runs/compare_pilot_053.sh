#!/bin/bash
H=/mnt/e/Ciencia/noturno/2022-qu-particle-transformer
$H/env/.venv/bin/python -I $H/runs/compare_perjet.py $H/runs/pilot_ParT_fp32 $H/runs/pilot_ParT_fp32_weaver0.5.3 $H/runs/compare_pilot_weaver0417_vs_053.json
