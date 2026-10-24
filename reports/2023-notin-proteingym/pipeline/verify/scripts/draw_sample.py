# Fixed-seed random order of the 217 assays, drawn before any score was computed or read.
# If the GPU budget forces a subset for the larger ESM2 models, we take the first k of this order
import sys
import numpy as np
import pandas as pd

ReferencePath = sys.argv[1]
OutputPath = sys.argv[2]
Reference = pd.read_csv(ReferencePath)
Generator = np.random.default_rng(0)
Order = Generator.permutation(len(Reference))
Output = pd.DataFrame({"rank": np.arange(len(Order)), "dms_index": Order, "DMS_id": Reference["DMS_id"].values[Order], "seq_len": Reference["seq_len"].values[Order]})
Output.to_csv(OutputPath, index=False)
print(Output.head(10))
