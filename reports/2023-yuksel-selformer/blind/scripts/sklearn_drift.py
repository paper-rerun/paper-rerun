"""Was the authors' ROC line ever runnable? Same object-dtype frame, several sklearn versions."""
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import roc_auc_score

smiles = ["CC", "CCO", "CCC", "CN"]
targets = [np.array([0], dtype=object), np.array([1], dtype=object),
           np.array([1], dtype=object), np.array([0], dtype=object)]
df = pd.DataFrame(np.column_stack([smiles, targets]), columns=["smiles", "target"])
test_y = pd.DataFrame(df.target, columns=["target"])
y_pred = np.array([0, 1, 0, 0])
print("sklearn", sklearn.__version__, "| dtype", test_y.dtypes.iloc[0])
try:
    print("  roc_auc_score ->", roc_auc_score(y_true=test_y, y_score=y_pred))
except Exception as exc:  # noqa: BLE001
    print("  %s: %s" % (type(exc).__name__, exc))
