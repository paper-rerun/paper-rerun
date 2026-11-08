"""Read the released checkpoints' trainer_state.json / training_args.bin.

Steps per epoch x train batch size recovers the size of the train fold the authors
actually used, which is the cheapest way to test whether our rebuilt split matches.
"""
import glob
import json
import math
import os

import torch

MODELS = r"E:\Ciencia\noturno\2023-yuksel-selformer-cego\downloads\models\classification_models"

for task_dir in sorted(glob.glob(os.path.join(MODELS, "SELFormer_*"))):
    print("=" * 70)
    print(os.path.basename(task_dir))
    ta = os.path.join(task_dir, "training_args.bin")
    if os.path.exists(ta):
        obj = torch.load(ta, map_location="cpu")
        d = obj.to_dict() if hasattr(obj, "to_dict") else vars(obj)
        keep = [
            "per_device_train_batch_size", "per_device_eval_batch_size", "num_train_epochs",
            "learning_rate", "weight_decay", "max_steps", "seed", "output_dir",
            "evaluation_strategy", "save_strategy", "fp16", "train_batch_size",
        ]
        print("  training_args:", {k: d[k] for k in keep if k in d})
    ma = os.path.join(task_dir, "model_args.json")
    if os.path.exists(ma):
        d = json.load(open(ma))
        keep = ["num_train_epochs", "train_batch_size", "learning_rate", "weight_decay",
                "warmup_steps", "warmup_ratio", "max_seq_length", "threshold", "output_dir", "fp16"]
        print("  model_args:", {k: d[k] for k in keep if k in d})
    for ts in glob.glob(os.path.join(task_dir, "checkpoint-*", "trainer_state.json")):
        st = json.load(open(ts))
        print("  checkpoint:", os.path.basename(os.path.dirname(ts)))
        print("   global_step", st.get("global_step"), "epoch", st.get("epoch"),
              "max_steps", st.get("max_steps"))
        logs = st.get("log_history", [])
        evals = [l for l in logs if "eval_loss" in l]
        print("   n_eval_entries", len(evals))
        if evals:
            print("   first eval:", {k: v for k, v in evals[0].items()
                                     if k in ("epoch", "step", "eval_roc-auc", "eval_accuracy",
                                              "eval_loss", "eval_runtime",
                                              "eval_samples_per_second")})
            best = max(evals, key=lambda l: l.get("eval_roc-auc", -1))
            print("   best eval roc-auc:", best.get("eval_roc-auc"), "at epoch", best.get("epoch"))
            print("   last eval roc-auc:", evals[-1].get("eval_roc-auc"))
            # steps per epoch -> train set size
            e1 = [l for l in evals if abs(l.get("epoch", 0) - 1.0) < 1e-6]
            if e1:
                spe = e1[0]["step"]
                print("   steps in epoch 1:", spe)
                for bs in (8, 16, 32):
                    print(f"     if train_batch_size={bs}: train size in "
                          f"[{(spe - 1) * bs + 1}, {spe * bs}]")
            # eval fold size from runtime metrics
            if "eval_runtime" in evals[0] and "eval_samples_per_second" in evals[0]:
                n = evals[0]["eval_runtime"] * evals[0]["eval_samples_per_second"]
                print("   implied eval(validation) fold size ~", round(n, 1),
                      "->", int(round(n)))
            if "eval_steps_per_second" in evals[0]:
                print("   eval steps/s", evals[0]["eval_steps_per_second"])
