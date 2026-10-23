"""Stream one test TSV from the HF dataset and keep every positive plus a Bernoulli(rate) sample of negatives.

The full test sets (2-19 GB, 4-35M windows) are too big to embed on one RTX 2070 SUPER, so we
estimate auPRC on a sample. Each kept row gets a uniform draw `u`, so a smaller nested sample is just
`u < smaller_rate`. Negatives are later weighted by 1/rate to keep the precision estimate unbiased.
"""
import random
import sys
import urllib.request

BaseUrl = "https://huggingface.co/datasets/kuleshov-group/cross-species-single-nucleotide-annotation/resolve/main/"


def main():
	RelativePath, NegativeRate, OutputPath = sys.argv[1], float(sys.argv[2]), sys.argv[3]
	RandomGenerator = random.Random(20261021)
	TotalRows = {"0": 0, "1": 0}
	KeptRows = {"0": 0, "1": 0}
	with urllib.request.urlopen(BaseUrl + RelativePath) as Response, open(OutputPath, "w") as Output:
		Header = Response.readline().decode().rstrip("\n").split("\t")
		LabelColumn = Header.index("label")
		Output.write("\t".join(Header + ["u"]) + "\n")
		for RawLine in Response:
			Line = RawLine.decode().rstrip("\n")
			Label = Line.split("\t", LabelColumn + 1)[LabelColumn]
			TotalRows[Label] += 1
			UniformDraw = RandomGenerator.random()
			# Keep every positive, sample negatives
			if Label == "1" or UniformDraw < NegativeRate:
				KeptRows[Label] += 1
				Output.write(f"{Line}\t{UniformDraw:.6f}\n")
	print(f"{RelativePath} rate={NegativeRate} total={TotalRows} kept={KeptRows}")


if __name__ == "__main__":
	main()
