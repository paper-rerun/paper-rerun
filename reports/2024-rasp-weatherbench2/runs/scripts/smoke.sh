#!/bin/bash
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
mkdir -p runs/smoke
export WB2_DATA_DIR=runs/smoke/data WB2_MAX_INITS=4
env/.venv/bin/python -I runs/scripts/wb2_rmse.py gs://weatherbench2/datasets/hres/2016-2022-0012-240x121_equiangular_with_poles_conservative.zarr gs://weatherbench2/datasets/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr geopotential 500 runs/smoke/hres_z500
