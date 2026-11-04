# Command-line part the authors' DAG passes to gwpopulation_pipe_analysis for this job (main.py at 83c9bb97)
PP_ARGS=(/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/data/pp_rerun.ini
  --label o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift
  --models SinglePeakSmoothedMassDistribution --models iid_spin_magnitude --models iid_spin_orientation --models gwpopulation.models.redshift.PowerLawRedshift
  --vt-models SinglePeakSmoothedMassDistribution --vt-models gwpopulation.models.redshift.PowerLawRedshift --vt-models iid_spin_orientation --vt-models iid_spin_magnitude)
