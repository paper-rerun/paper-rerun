#!/bin/bash
# Cross-check: official scripts/evaluate.py at 156e5dc (deterministic config, in-memory runner) on January 2020 inits
# Flags follow docs/source/official-evaluation.md (hres_vs_analysis 240x121), narrowed to geopotential 500 and one month
cd /mnt/e/Ciencia/noturno/2024-rasp-weatherbench2
export MPLBACKEND=Agg OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
mkdir -p runs/official
D=gs://weatherbench2/datasets
run_official() {
	local prefix=$1 forecast=$2 obs=$3 variable=$4 level=$5
	if [ -f runs/official/${prefix}deterministic.nc ]; then echo "skip $prefix"; return; fi
	echo "$(date -Is) start $prefix"
	env/.venv/bin/python repo/weatherbench2/scripts/evaluate.py \
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
		--use_beam=False
	echo "$(date -Is) end $prefix exit $?"
}
run_official hres_vs_analysis_2020jan_z500_ $D/hres/2016-2022-0012-240x121_equiangular_with_poles_conservative.zarr $D/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr geopotential 500
run_official pangu_vs_era_2020jan_t850_ $D/pangu/2018-2022_0012_240x121_equiangular_with_poles_conservative.zarr $D/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr temperature 850
