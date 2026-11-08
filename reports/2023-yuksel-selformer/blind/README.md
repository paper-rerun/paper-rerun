# Blind rerun

An independent reproduction of this paper, done by an agent that was not allowed to see the report
in the folder above, nor its scripts, its pre-registration or its adversarial review. It was given
the paper, the authors' repository address and the five published numbers. It downloaded the weights
again, built its own environment, wrote its own scoring code from the authors' training scripts, and
froze its own pre-registration (`claims.json`, SHA-256 in `claims.sha256`) before loading any model.

Both runs reached the same values: BBBP 0.8913, BACE 0.7104, Tox21 0.6131 and SIDER
0.718012171633844, against the paper's 0.902, 0.832, 0.653 and 0.745. On the two binary tasks the
two runs agree to 16 digits. The one difference is the probability-variant AUC for SIDER, 0.7801 in
the first run against 0.7781 here, because the stored scores saturate in float32 in one of them and
ties cost AUC; the metric that decides the verdict is identical.

This run added three findings, all of them in the report above: the README's scaffold command fails
on the line that prints the table's number, on four scikit-learn versions including the authors'
pinned one; the best model was never saved, so BACE's best validation epoch is not in the download;
and no multi-label threshold brings SIDER up to the published value.

What is here: the pre-registration and its hash, the lockfiles, the scoring and checking scripts,
the per-task results, the logs including the traceback of the README command, and the hashes of the
downloaded archives. The environment itself is not committed — the lockfiles rebuild it.
