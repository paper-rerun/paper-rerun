# GPU budget estimate from sequence lengths and the synthetic benchmark (logs/bench.log); no scores involved
import json, sys
import numpy as np
import pandas as pd

Reference = pd.read_csv("/mnt/e/Ciencia/pipeline/2023-notin-proteingym/repo/reference_files/DMS_substitutions.csv")
Order = json.load(open("sample_order.json"))["order"]
Bench = {}
for Line in open("logs/bench.log"):
	Parts = Line.split()
	if len(Parts) == 4 and Parts[2] == "s/pass":
		Bench.setdefault(Parts[0], {})[int(Parts[1])] = float(Parts[3])
Overhead = {"esm2_t6_8M_UR50D": 50, "esm2_t12_35M_UR50D": 55, "esm2_t30_150M_UR50D": 65, "esm2_t33_650M_UR50D": 90}
for Name, Table in Bench.items():
	Lengths = sorted(Table)
	PassCount = Reference["seq_len"] + 2
	WindowLength = np.minimum(Reference["seq_len"], 1022)
	PerPass = np.interp(WindowLength, Lengths, [Table[Length] for Length in Lengths])
	PerAssay = PassCount * PerPass + Overhead[Name]
	Cumulative = np.cumsum(PerAssay.values[Order])
	print(Name, "full h", round(PerAssay.sum() / 3600, 2), "| first 30/50/80 in order h",
		[round(Cumulative[N - 1] / 3600, 2) for N in (30, 50, 80)])
