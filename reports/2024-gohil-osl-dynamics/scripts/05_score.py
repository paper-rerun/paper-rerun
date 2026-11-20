"""Score the frozen claims, and say plainly which of them the deposit can answer.

Run after 01, 02 and 04. It verifies the claims hash first, then scores.
"""

import glob
import hashlib
import json

CLAIMS = "claims.json"
EXPECTED_SHA = "e1df8bd22acf7a57271d2f4f44604a4291b79a6b360be36ec6108d0870a29a6c"

digest = hashlib.sha256(open(CLAIMS, "rb").read()).hexdigest()
if digest != EXPECTED_SHA:
	raise SystemExit(f"claims.json changed since it was frozen: {digest}")
print(f"claims.json verified: {digest}")

claims = json.load(open(CLAIMS))
groups = json.load(open("runs/out/groups.json"))
audit = json.load(open("runs/out/model_audit.json"))

STAT_INDEX = {"fractional_occupancy": 0, "mean_lifetime": 1, "mean_interval": 2, "switching_rate": 3}

verdict = {}

# C6 is the one claim that needs nothing but the demographics file
verdict["C6"] = {
	"scoreable": True,
	"reproduces": groups["C6_reproduces"],
	"found": [groups["n_young"], groups["n_old"]],
	"published": [groups["published_n_young"], groups["published_n_old"]],
}

# C1 to C5 name states by index. The index only means something inside one fit.
giles = audit["deposited"]["tde_hmm_notts_meguk_giles"]
why_not = (
	f"The frozen rule was to read the states in the order the deposited model stores them. "
	f"The one deposited model on the paper's parcellation has {giles['n_states']} states, not the 8 "
	f"the figure's script asks for, and carries no PCA basis, so its states cannot be mapped onto "
	f"the data. The 8-state state time courses that are deposited cover 5 of the 65 subjects, which "
	f"is not enough for a group test. So no state in the deposit is the paper's state 4, 6, 1 or 8."
)
for cid in ["C1", "C2", "C3", "C4", "C5"]:
	claim = next(c for c in claims["claims"] if c["id"] == cid)
	verdict[cid] = {
		"scoreable_from_the_deposit": False,
		"why": why_not,
		"claim": claim["text"],
	}

# C7 needs a DyNeMo fit over all 65 subjects, and the deposit has covariances and free
# energies for 20 runs but no mode time courses.
verdict["C7"] = {
	"scoreable_from_the_deposit": False,
	"why": (
		"The DyNeMo deposit holds covariances and free energies for 20 runs, and mode time "
		"courses for 5 subjects. The claim is about a group difference over 65. Declared in "
		"claims.json as not checkable rather than failed."
	),
}

# What our own re-fits can say, label free. This is a post-hoc reading, forced by the state
# identity problem above, and it is marked as such: it asks the weaker question the paper's
# sentence implies, not the one the frozen claim asks.
refits = sorted(glob.glob("runs/out/stats_seed*.json"))
label_free = []
for path in refits:
	s = json.load(open(path))
	tests = s["readings"]["viterbi"]["tests"]
	n_states = s["n_states"]
	entry = {"seed": s["seed"], "n_states": n_states}
	for name, direction in [
		("fractional_occupancy", "up"),
		("switching_rate", "up"),
		("mean_lifetime", "down"),
		("mean_interval", "either"),
	]:
		i = STAT_INDEX[name]
		hits = []
		for state in range(n_states):
			ps = [t["pvalues"][i][state] for t in tests]
			cope = tests[0]["copes"][i][state]
			if max(ps) >= 0.05:
				continue
			if direction == "up" and cope <= 0:
				continue
			if direction == "down" and cope >= 0:
				continue
			hits.append({"state": state + 1, "cope_old_minus_young": cope, "pvalues": ps})
		entry[name] = {"direction_asked": direction, "n_states_significant": len(hits), "states": hits}
	label_free.append(entry)

out = {
	"claims_sha256": digest,
	"frozen_at": open("claims.frozen_at.txt").read().strip(),
	"verdict": verdict,
	"n_claims_scoreable": sum(1 for v in verdict.values() if v.get("scoreable") or v.get("scoreable_from_the_deposit")),
	"n_claims": len(verdict),
	"post_hoc_label_free_refit": label_free,
	"post_hoc_note": (
		"Label free, and post hoc. State numbers are arbitrary in a fresh fit, so instead of "
		"asking whether state 4 moved we ask whether any state moved in the direction the "
		"paper reports, at the threshold it reports, under its own test. That is a weaker "
		"question than the frozen claim, and it is reported separately for that reason."
	),
}
with open("runs/out/verdict.json", "w") as fh:
	json.dump(out, fh, indent=1)

print()
for cid in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
	v = verdict[cid]
	if cid == "C6":
		print(f"{cid}: {'reproduces' if v['reproduces'] else 'FAILS'} ({v['found']} against {v['published']})")
	else:
		print(f"{cid}: not scoreable from the deposit")
print()
for entry in label_free:
	print(f"re-fit seed {entry['seed']}, {entry['n_states']} states:")
	for name in ["fractional_occupancy", "switching_rate", "mean_lifetime", "mean_interval"]:
		block = entry[name]
		states = ", ".join(str(h["state"]) for h in block["states"]) or "none"
		print(f"  {name} ({block['direction_asked']}): {block['n_states_significant']} significant, states {states}")
