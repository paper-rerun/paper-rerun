No source patches. gwpopulation_pipe 83c9bb97 and gwpopulation 0.6.3 (PyPI) ran unmodified.
The only additions are outside the authors' code:
- runs/run_pp.py: calls np.random.seed(<seed>) and then gwpopulation_pipe.data_analysis.main()
- runs/prep_data.py: writes the published per-event arrays ('original' group of the released _samples.hdf5) in the pickle format main() reads
- data/pp_rerun.ini and data/pp_published.prior: run options and the priors stored in the published result.json
