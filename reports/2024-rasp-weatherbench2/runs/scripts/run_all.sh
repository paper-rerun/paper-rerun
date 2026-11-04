#!/bin/bash
# Full run, restartable: each task appends per-init MSE to runs/out/<task>.jsonl and skips what is already there
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
export MPLBACKEND=Agg OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
mkdir -p runs/out runs/logs
D=gs://weatherbench2/datasets
HRES=$D/hres/2016-2022-0012-240x121_equiangular_with_poles_conservative.zarr
HRES_T0=$D/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr
ERA5=$D/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr
PANGU=$D/pangu/2018-2022_0012_240x121_equiangular_with_poles_conservative.zarr
GC=$D/graphcast/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr
PANGU_OPER=$D/pangu_hres_init/2020_0012_240x121_equiangular_with_poles_conservative.zarr
GC_OPER=$D/graphcast_hres_init/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr
NGCM=$D/neuralgcm_deterministic/2020-240x121_equiangular_with_poles_conservative.zarr

run() {
	local name=$1
	if [ -f runs/out/$name.summary.json ]; then echo "skip $name (done)"; return; fi
	echo "$(date -Is) start $name"
	env/.venv/bin/python -I runs/scripts/wb2_rmse.py "$2" "$3" "$4" "$5" runs/out/$name > runs/logs/$name.log 2>&1
	# Keep the exit code before $(date) runs: the substitution resets $? (every "exit 0" in the first run_all.log is meaningless)
	local rc=$?
	echo "$(date -Is) end $name rc=$rc"
}
free_gb() { df -BG --output=avail /mnt/e | tail -1 | tr -dc 0-9; }

run hres_z500 $HRES $HRES_T0 geopotential 500
run pangu_z500 $PANGU $ERA5 geopotential 500
run graphcast_z500 $GC $ERA5 geopotential 500
echo "free on E: $(free_gb) GB"
if [ "$(free_gb)" -lt 40 ]; then echo "less than 40 GB free, stopping before T850"; exit 0; fi
run hres_t850 $HRES $HRES_T0 temperature 850
run pangu_t850 $PANGU $ERA5 temperature 850
run graphcast_t850 $GC $ERA5 temperature 850
run panguoper_z500 $PANGU_OPER $HRES_T0 geopotential 500
run graphcastoper_z500 $GC_OPER $HRES_T0 geopotential 500
run neuralgcm_z500 $NGCM $ERA5 geopotential 500
run neuralgcm_t850 $NGCM $ERA5 temperature 850
echo "$(date -Is) all done"
