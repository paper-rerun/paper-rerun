# Builds claims.json from the paper values only (no model output is read here)
import json
import math

N_QCD_TEST = 2_000_000

# Table 1, column order: Hbb, Hcc, Hgg, H4q, Hqql, Tbqq, Tbl, Wqq, Zqq
REJ_COLUMNS = [
    ("Hbb", "H->bb", "label_Hbb", "HToBB", 50.0),
    ("Hcc", "H->cc", "label_Hcc", "HToCC", 50.0),
    ("Hgg", "H->gg", "label_Hgg", "HToGG", 50.0),
    ("H4q", "H->4q", "label_H4q", "HToWW4Q", 50.0),
    ("Hqql", "H->lnuqq'", "label_Hqql", "HToWW2Q1L", 99.0),
    ("Tbqq", "t->bqq'", "label_Tbqq", "TTBar", 50.0),
    ("Tbl", "t->blnu", "label_Tbl", "TTBarLep", 99.5),
    ("Wqq", "W->qq'", "label_Wqq", "WToQQ", 50.0),
    ("Zqq", "Z->qq", "label_Zqq", "ZToQQ", 50.0),
]

MODELS = {
    "ParT": {
        "priority_acc_auc": "primary",
        "priority_rej": "secondary",
        "acc": 0.861,
        "auc": 0.9877,
        "rej": [10638, 4149, 123, 1864, 5479, 32787, 15873, 543, 402],
        "conditions": {
            "model": "ParT, full input (kinematics + particle ID + trajectory displacement, 17 particle features of data/JetClass/JetClass_full.yaml), network config networks/example_ParticleTransformer.py (ParticleTransformerWrapper -> weaver.nn.model.ParticleTransformer, 8 particle blocks, 2 class blocks, embed [128,512,128], pair embed [64,64,64], 8 heads)",
            "checkpoint": "models/ParT_full.pt from jet-universe/particle_transformer @ 2925bdb249e8ef78560cc2b9b651eda3615da8c7 (unchanged since initial commit 512fcd14b3a0e1e0487c6f357b9c72858d14d26d, 2022-03-27); 8,655,467 B; md5 719fb783d8eeb27f609b103a82e100f6; sha256 61e752f80d7c237d4b18b97705df416a8518dd9e3d5a78a8bbdeebadd787fec0; loaded strictly with load_state_dict (weaver --predict with a .pt model prefix)",
            "precision": "fp32 (no --use-amp) as the main run; AMP (--use-amp) as a pre-registered variant, see definition D9",
        },
    },
    "ParticleNet": {
        "priority_acc_auc": "optional",
        "priority_rej": "optional",
        "acc": 0.844,
        "auc": 0.9849,
        "rej": [7634, 2475, 104, 954, 3339, 10526, 11173, 347, 283],
        "conditions": {
            "model": "ParticleNet, full input, network config networks/example_ParticleNet.py (weaver.nn.model.ParticleNet), same data config data/JetClass/JetClass_full.yaml",
            "checkpoint": "models/ParticleNet_full.pt from the same commit (unchanged since initial commit 512fcd1); 1,522,482 B; md5 581175b6bd8655a4b7021885218db933; sha256 375b81543769f4a0bd2de9818c5885a04c735b5462a64dcadc2a088edaf3d1d2",
            "precision": "fp32 only (train_JetClass.sh passes --use-amp for ParT but not for PN)",
        },
    },
}

COMMON_CONDITIONS = {
    "test_set": "JetClass v1.0.0 (Zenodo 10.5281/zenodo.6619768, CC-BY-4.0), file JetClass_Pythia_test_20M.tar, 30,370,816,000 B, md5 64e5156d26d101adeb43b8388207d767; all ROOT files under test_20M/, all jets, no selection; must contain exactly 2,000,000 jets per class and 20,000,000 in total (D1)",
    "samples": "20,000,000 jets (10 classes x 2,000,000); Rej uses the 2,000,000 signal-class jets plus the 2,000,000 QCD (ZJetsToNuNu) jets",
    "software": "weaver-core 0.4.17 (git 9b92955bc89ecada29f5d4e6b9a21f4f0a28f8c5) main; weaver-core 0.5.3 as variant (D10)",
    "command": "weaver --predict --data-test 'HToBB:<dir>/test_20M/HToBB_*.root' ... (10 groups as in train_JetClass.sh) --data-config data/JetClass/JetClass_full.yaml --network-config <network config> --model-prefix <checkpoint .pt> --gpus 0 --batch-size 512 --predict-output pred.root",
}


def fmt_band(value, rel):
    return [round(value * (1 - rel), 1), round(value * (1 + rel), 1)]


def build_claims():
    claims = []
    for model_name, model in MODELS.items():
        conditions = dict(COMMON_CONDITIONS)
        conditions.update(model["conditions"])

        claims.append({
            "id": f"{model_name}.accuracy",
            "priority": model["priority_acc_auc"],
            "quantity": "Accuracy, all classes",
            "paper_value": model["acc"],
            "unit": "fraction (dimensionless)",
            "location": f"Table 1, row '{model_name}', column 'All classes / Accuracy'; PMLR PDF page 7 (proceedings p. 18287); identical in arXiv 2202.03772 v3 Table 1; repeated in Table 3 bold row (100 M)",
            "definition": "D3",
            "tolerance": {
                "exact": "ours rounds to the paper value at 3 decimals, i.e. 0.8605 <= ours < 0.8615 for ParT" if model_name == "ParT" else "ours rounds to the paper value at 3 decimals",
                "pass": "|ours - paper| <= 0.001 (one unit in the last reported digit)",
                "fail": "|ours - paper| > 0.001",
                "basis": "Same checkpoint and same full test set, so sampling error does not apply; the only expected differences are rounding of the reported value (+-0.0005) and numerical drift from precision (fp32 vs AMP) and library versions. One unit in the last reported digit covers both. For scale only: the binomial standard error of an accuracy of 0.861 on 20 M jets is 7.7e-5.",
            },
            "conditions": conditions,
        })

        claims.append({
            "id": f"{model_name}.auc",
            "priority": model["priority_acc_auc"],
            "quantity": "AUC, all classes (macro one-vs-one)",
            "paper_value": model["auc"],
            "unit": "dimensionless",
            "location": f"Table 1, row '{model_name}', column 'All classes / AUC'; PMLR PDF page 7 (proceedings p. 18287); definition in footnote 3, page 3",
            "definition": "D4",
            "tolerance": {
                "exact": "ours rounds to the paper value at 4 decimals",
                "pass": "|ours - paper| <= 0.0001 (one unit in the last reported digit)",
                "fail": "|ours - paper| > 0.0001",
                "basis": "Same reasoning as accuracy: same checkpoint and test set; rounding (+-0.00005) plus small numerical drift.",
            },
            "conditions": conditions,
        })

        for (short, pretty, label, file_prefix, tpr), rej in zip(REJ_COLUMNS, model["rej"]):
            # Number of QCD test jets passing the cut implied by the paper value
            implied_background_count = round(N_QCD_TEST / rej)
            rel_1sigma = 1.0 / math.sqrt(implied_background_count)
            rel_rounding = 0.5 / rej
            rel_pass = max(rel_1sigma, rel_rounding)
            tpr_label = ("%g" % tpr)
            claims.append({
                "id": f"{model_name}.rej{tpr_label}_{short}",
                "priority": model["priority_rej"],
                "quantity": f"Background (q/g) rejection Rej{tpr_label}% for {pretty} vs QCD",
                "paper_value": rej,
                "unit": "dimensionless (1/FPR)",
                "location": f"Table 1, row '{model_name}', column '{pretty} Rej{tpr_label}%'; PMLR PDF page 7 (proceedings p. 18287); definition eq. (1)-(2), page 3",
                "definition": "D5, D6, D7, D8",
                "signal_class": {"label": label, "files": f"test_20M/{file_prefix}_*.root", "tpr": tpr / 100.0},
                "implied_qcd_count_passing": implied_background_count,
                "tolerance": {
                    "exact": f"the number of QCD jets passing the threshold equals {implied_background_count} (paper value = round(2,000,000 / {implied_background_count}))",
                    "pass": f"|ours/paper - 1| <= {rel_pass:.4f}, i.e. Rej in {fmt_band(rej, rel_pass)}",
                    "marginal": f"{rel_pass:.4f} < |ours/paper - 1| <= {2 * rel_pass:.4f}, i.e. Rej in {fmt_band(rej, 2 * rel_pass)} but outside the pass band",
                    "fail": f"|ours/paper - 1| > {2 * rel_pass:.4f}",
                    "basis": f"Rej = 2,000,000 / k with k = {implied_background_count} QCD jets above the cut. Same checkpoint and test set should give the same k up to numerical drift; the paper gives no uncertainty, so the band is the Poisson relative error 1/sqrt(k) = {rel_1sigma:.4f} (or the rounding of the reported integer, {rel_rounding:.5f}, whichever is larger). This is the scale on which a different but equivalent checkpoint or a few tied/shifted scores would move the number; few-jet values (k < 200) are fragile by construction.",
                },
                "conditions": conditions,
            })
    return claims


DEFINITIONS = [
    {
        "id": "D1",
        "choice": "Test set",
        "value": "The whole JetClass_Pythia_test_20M.tar (JetClass v1.0.0, Zenodo 6619768), every jet in every test_20M/*.root file, no subsampling, no selection (the yaml 'selection' block is empty and --extra-test-selection is not used; --data-fraction stays at its default 1). Count after extraction and before scoring: must be 2,000,000 per class and 20,000,000 in total, otherwise stop and report.",
        "quote": "For the evaluation of performance, a separate test set with 2 M jets in each class (in total 20 M) is provided. (Section 2, p. 3)",
        "ambiguity": "The paper v1 (Feb 2022) predates the public Zenodo release (June 2022, v1.0.0); we assume the released test set is the one behind Table 1 (Table 1 is identical in arXiv v3 and PMLR, both of which cite the Zenodo record). Supporting evidence from the paper's own numbers: all 45 Rej values of Table 1 (5 models x 9 columns) equal round(2,000,000/k) for an integer k, consistent with exactly 2,000,000 QCD jets in the test set.",
    },
    {
        "id": "D2",
        "choice": "File-to-label mapping and output order",
        "value": "ZJetsToNuNu -> label_QCD (background), HToBB -> Hbb, HToCC -> Hcc, HToGG -> Hgg, HToWW4Q -> H4q, HToWW2Q1L -> Hqql (H->lnuqq'), ZToQQ -> Zqq, WToQQ -> Wqq, TTBar -> Tbqq, TTBarLep -> Tbl (t->blnu). Model outputs in the order of data/JetClass/JetClass_full.yaml labels.value: [label_QCD, label_Hbb, label_Hcc, label_Hgg, label_H4q, label_Hqql, label_Zqq, label_Wqq, label_Tbqq, label_Tbl]. True label = the label_* branch stored in each file (not the file name); the file name is used only as a cross-check.",
        "quote": "By default, the q/g jets are considered as the background, as is the case in most LHC data analyses, and each of the other 9 types of jets can be considered as the signal. (Section 2, p. 3)",
        "ambiguity": "None expected: mapping comes from train_JetClass.sh and JetClass_full.yaml in the authors' repo. Any jet whose label branch disagrees with its file name is counted and reported.",
    },
    {
        "id": "D3",
        "choice": "Accuracy",
        "value": "Top-1 accuracy: fraction of the 20,000,000 test jets for which argmax over the 10 softmax outputs equals the true class index (numpy argmax, first index on exact ties). Computed on all 10 prediction groups concatenated.",
        "quote": "two common metrics, i.e., the accuracy and the area under the ROC curve (AUC) are adopted to quantify the overall performance. (Section 2, p. 3)",
        "ambiguity": "The paper does not spell out top-1, but for a 10-class classifier with one label per jet that is the only standard reading. weaver's own per-group log metric is not used, because each --data-test group holds a single class.",
    },
    {
        "id": "D4",
        "choice": "AUC",
        "value": "sklearn.metrics.roc_auc_score(y_true, scores, average='macro', multi_class='ovo') with y_true the integer class index (0..9 in the D2 order) and scores the N x 10 softmax matrix, on all 20,000,000 jets at once. Scores are cast to float64; if sklearn rejects rows that do not sum to 1 within its tolerance, each row is divided by its sum (numerical only, argmax and ranking unchanged).",
        "quote": "The AUC can be calculated using roc_auc_score in scikit-learn with average='macro' and multi_class='ovo'. (footnote 3, p. 3)",
        "ambiguity": "Low. weaver-core's built-in 'roc_auc_score' metric is functools.partial(roc_auc_score, multi_class='ovo') with the default average='macro', the same definition. sklearn version is recorded.",
    },
    {
        "id": "D5",
        "choice": "Rej definition and populations",
        "value": "For each signal class S: take only jets whose true class is S (2,000,000) or QCD (2,000,000). Rej = 1/FPR, where FPR is the fraction of QCD jets passing the threshold at which the signal efficiency (TPR) equals X. X = 50% for Hbb, Hcc, Hgg, H4q, Tbqq, Wqq, Zqq; 99% for Hqql; 99.5% for Tbl.",
        "quote": "RejX% = 1/FPR at TPR = X% (1) ... It is increased to 99% (99.5%) for H -> lnuqq' (t -> blnu) ... Since the definition of the RejX metric involves only two classes, i.e., the signal class under consideration (S) and the background class (B), the TPR and FPR are evaluated using a two-class score (Section 2, p. 3)",
        "ambiguity": "None on populations. Jets of the other 8 classes are excluded, not counted as background.",
    },
    {
        "id": "D6",
        "choice": "Two-class score",
        "value": "score_SvsB = s_S / (s_S + s_QCD), with s_S and s_QCD the softmax outputs of the 10-class model, computed in float64 from the stored float32 softmax (main). Variants, reported side by side: (a) the same ratio in float32, as a literal numpy implementation on weaver's float32 output would compute it; (b) the rank-equivalent log s_S - log s_QCD in float64, which has no saturation at 1.0. All three give the same ROC in exact arithmetic; differences can only come from ties created by rounding, and the number of tied jets at the chosen threshold is reported.",
        "quote": "scoreSvsB = score(S) / (score(S) + score(B)), (2) where score(S) and score(B) are the softmax outputs for class S and B, respectively (Section 2, p. 3)",
        "ambiguity": "The paper does not say in which precision the ratio was computed. For highly separated classes (t->blnu at 99.5%, t->bqq' and H->bb at 50%) many signal scores sit near 1.0 and float32 rounding can create ties that move the ROC point by a few QCD jets, which matters when only 61-188 QCD jets pass. weaver stores softmax as float32 (torch.softmax(logits.float())). The float64 ratio is the main value; if the variants disagree beyond the tolerance, all are reported and the claim is judged on the main value.",
    },
    {
        "id": "D7",
        "choice": "Reading FPR at TPR = X (operating point)",
        "value": "Main: sklearn.metrics.roc_curve(y, score_SvsB, drop_intermediate=False) (y = 1 for S, 0 for QCD); take the first ROC point with TPR >= X and its FPR (threshold rule score >= t). Second, also reported: linear interpolation np.interp(X, tpr, fpr) on the same curve. Third, also reported: the ROC point with TPR closest to X. Report k = FPR x 2,000,000 for each.",
        "quote": "we propose the background rejection (i.e., the inverse of the false positive rate) at a certain signal efficiency (i.e., the true positive rate, TPR) of X% (Section 2, p. 3)",
        "ambiguity": "The paper does not say whether FPR is interpolated or read at the nearest ROC point. With exactly 2,000,000 signal jets, TPR = 50%, 99% and 99.5% fall exactly on a ROC point (1,000,000, 1,980,000 and 1,990,000 signal jets), so the three readings coincide unless scores are tied at the threshold. The paper's own numbers fit this: every Table 1 Rej equals round(2,000,000/k) for an integer k (ParT: k = 188, 482, 16260, 1073, 365, 61, 126, 3683, 4975), i.e. FPR is a whole count of QCD jets over 2,000,000 and not a smoothed value. This was checked from the paper values only, not from anything we computed.",
    },
    {
        "id": "D8",
        "choice": "Rej rounding",
        "value": "Rej reported as 1/FPR to one decimal and compared with the integer in Table 1; k (the QCD count) reported as an integer.",
        "quote": "Table 1 reports Rej as integers (e.g. ParT H->bb Rej50% 10638).",
        "ambiguity": "None.",
    },
    {
        "id": "D9",
        "choice": "Numerical precision of inference",
        "value": "Main: fp32 (weaver --predict without --use-amp). Variant: the same command with --use-amp (torch autocast fp16 inside the ParT forward pass). ParticleNet: fp32 only. Decision rule fixed now: a ParT claim counts as reproduced if the fp32 value passes; if fp32 fails and AMP passes, it is reported as 'reproduced under the authors' AMP setting', not as a plain reproduction.",
        "quote": "We implement the ParT model in PyTorch (Section 4, p. 6). The paper does not mention mixed precision.",
        "ambiguity": "train_JetClass.sh passes --use-amp for ParT (not for PN, PFN, PCNN), and the same command also runs the test prediction after training (--data-test ... --predict-output pred.root). In weaver, --use-amp sets use_amp=True in the network, which also enables autocast at prediction time. So the authors' own Table 1 evaluation of ParT was probably under AMP. fp32 is kept as the main run because it is the deterministic, version-independent baseline; the AMP variant is the closer copy of the authors' setup. The old weaver used in early 2022 may have handled AMP differently; not checkable.",
    },
    {
        "id": "D10",
        "choice": "Framework version",
        "value": "weaver-core 0.4.17 (last 0.4.x, numpy<2) main; weaver-core 0.5.3 variant. Batch size 512 as in train_JetClass.sh. --num-workers chosen for the environment (0 if the loader hangs, weaver-core issue #14); it does not change per-jet outputs. Input length 128 particles, pad_mode 'wrap' for points/features/vectors and 'constant' for the mask, exactly as in JetClass_full.yaml; not modified.",
        "quote": "We implement the ParT model in PyTorch (Paszke et al., 2019). Specifically, the P-MHA is implemented using the PyTorch's MultiheadAttention by providing the interaction matrix U as the attn_mask input. (Section 4, p. 6) ... we use the full set of particle features, including kinematics, particle identification, and trajectory displacement, as inputs. The full list of 17 features for each particle is summarized in Table 2. (Section 5.1, p. 6)",
        "ambiguity": "The paper predates weaver-core (Table 1 was made with the older hqucms/weaver; this repo moved to weaver-core>=0.4 on 2022-12-15, commit 29ef32b5). weaver/nn/model/ParticleTransformer.py changes substantially between 0.4.17 and 0.5.3 (git diff: ~1,559 lines), so 0.5.3 is a variant, not the reference. Any failure to load the checkpoint strictly is reported, never worked around by editing the model.",
    },
    {
        "id": "D11",
        "choice": "Checkpoint identity",
        "value": "models/ParT_full.pt (and ParticleNet_full.pt) is taken as the checkpoint behind Table 1.",
        "quote": "The checkpoint with the highest accuracy on the validation set is used to evaluate the final performance on the test set. (Section 5.1, p. 6)",
        "ambiguity": "The README calls the .pt files 'pre-trained models' for fine-tuning and does not state that ParT_full.pt is the Table 1 checkpoint. Its date (initial commit 2022-03-27, seven weeks after arXiv v1) and architecture match. If accuracy matches at 3 decimals and the Rej counts match k exactly or nearly, it is the same model; a small systematic offset would point first to a different checkpoint, before any code issue.",
    },
    {
        "id": "D12",
        "choice": "Author per-item results",
        "value": "None used.",
        "quote": "n/a",
        "ambiguity": "The authors publish no per-jet predictions, scores, ROC curves or source data for Table 1 (repo, Zenodo record and paper checked during triage and again here). Nothing was downloaded into sources/; tolerances rest on rounding, Poisson counting and the integer-k pattern in the paper's own table.",
    },
]


def main():
    document = {
        "paper": {
            "citation": "Qu, H., Li, C., Qian, S. Particle Transformer for Jet Tagging. Proceedings of the 39th International Conference on Machine Learning (ICML 2022), PMLR 162:18281-18292",
            "pdf": "https://proceedings.mlr.press/v162/qu22b/qu22b.pdf",
            "pdf_sha256": "7ecc948f260db90c2159da06982caacb8684c9064315b7514e768b0e319a1dd5",
            "arxiv": "2202.03772 v3",
            "arxiv_pdf_sha256": "c39a85bc64e950e5754ea1b692a59ffd0c13b540d1920cad5f8f000888c35a9b",
            "supplementary": "None. The PMLR paper has no appendix; arXiv v3 has none either.",
            "code": "https://github.com/jet-universe/particle_transformer @ 2925bdb249e8ef78560cc2b9b651eda3615da8c7",
            "dataset": "JetClass v1.0.0, DOI 10.5281/zenodo.6619768, CC-BY-4.0",
        },
        "target": "Table 1, ParT row (full input), released checkpoint models/ParT_full.pt, full JetClass test set (20 M jets). Primary: Accuracy and AUC. Secondary: 9 background rejections. Optional: ParticleNet row with models/ParticleNet_full.pt.",
        "verdict_rule": "Reproduced: both primary ParT claims pass. Partially reproduced: one primary passes, or both pass but more than 2 of the 9 ParT Rej claims fail. Not reproduced: both primary claims fail. Secondary and optional claims are reported one by one and do not override the primary verdict.",
        "claims": build_claims(),
        "definitions": DEFINITIONS,
        "pre_registered": "2026-10-25, before any model was run or any test data downloaded in this project",
    }
    with open("claims.json", "w", encoding="utf-8", newline="\n") as output_file:
        json.dump(document, output_file, indent=2, ensure_ascii=False)
        output_file.write("\n")


if __name__ == "__main__":
    main()
