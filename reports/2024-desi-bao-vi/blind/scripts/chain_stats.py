"""Weighted mean/sd of cobaya-format chains (ours and, as labelled diagnostic, DESI's)"""
import glob
import sys

import numpy as np


def ReadChains(Prefix, BurnFraction):
	Header = open(glob.glob(Prefix + ".1.txt")[0]).readline().lstrip("#").split()
	Rows = []
	for Path in sorted(glob.glob(Prefix + ".[0-9].txt")):
		Data = np.loadtxt(Path)
		Rows.append(Data[int(BurnFraction * len(Data)):])
	return Header, np.vstack(Rows)


Prefix = sys.argv[1]
Burn = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
Header, Data = ReadChains(Prefix, Burn)
Weights = Data[:, Header.index("weight")]
print(Prefix, "burn", Burn, "rows", len(Data), "sum weights", Weights.sum())
for Name in sys.argv[3:]:
	if Name not in Header:
		print(Name, "not in chain")
		continue
	Values = Data[:, Header.index(Name)]
	Mean = np.average(Values, weights=Weights)
	Sd = np.sqrt(np.average((Values - Mean) ** 2, weights=Weights))
	print(f"{Name}: {Mean:.5f} +/- {Sd:.5f}")
