# Pre-registered assay order for the larger ESM2 sizes, drawn before any ESM2 score (ours or the authors') was looked at
# A random permutation of the 217 DMS_index values, Python random seed 0. If the GPU budget does not allow all 217,
# the sample is the first N of this order, N fixed in sample.json before the runs start
import json, random, sys
import pandas as pd

Reference = pd.read_csv(sys.argv[1])
Order = list(range(len(Reference)))
random.Random(0).shuffle(Order)
json.dump({"seed": 0, "method": "random.Random(0).shuffle(list(range(217)))", "order": Order,
	"DMS_id_order": [Reference.loc[Index, "DMS_id"] for Index in Order]}, open("sample_order.json", "w"), indent=1)
print(Order[:40])
