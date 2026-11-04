#!/bin/bash
# Cross-check added in the revision: official scripts/evaluate.py at 156e5dc on January 2020 inits for the two GraphCast stores
# Same flags as official_subset.sh. Differences: dask capped at 8 workers, real exit code, peak RSS from /usr/bin/time -v (appended)
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
export MPLBACKEND=Agg OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 DASK_NUM_WORKERS=8
mkdir -p runs/official
D=gs://weatherbench2/datasets
LOG=runs/logs/official_subset_graphcast.log
run_official() {
	local prefix=$1 forecast=$2 obs=$3 variable=$4 level=$5
	if [ -f runs/official/${prefix}deterministic.nc ]; then echo "skip $prefix" >> $LOG; return; fi
	echo "$(date -Is) start $prefix" >> $LOG
	/usr/bin/time -v env/.venv/bin/python repo/weatherbench2/scripts/evaluate.py \
		--forecast_path=$forecast \
		--obs_path=$obs \
		--climatology_path=$D/era5-hourly-climatology/1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr \
		--output_dir=runs/official/ \
		--output_file_prefix=$prefix \
		--input_chunks=init_time=1 \
		--regions=global \
		--eval_configs=deterministic \
		--evaluate_climatology=False \
		--evaluate_persistence=False \
		--time_start=2020-01-01 \
		--time_stop=2020-01-31 \
		--variables=$variable \
		--levels=$level \
		--use_beam=False >> $LOG 2>&1
	local rc=$?
	echo "$(date -Is) end $prefix rc=$rc" >> $LOG
}
run_official graphcast_vs_era_2020jan_z500_ $D/graphcast/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr $D/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr geopotential 500
run_official graphcastoper_vs_analysis_2020jan_z500_ $D/graphcast_hres_init/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr $D/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr geopotential 500
echo "$(date -Is) all done" >> $LOG
