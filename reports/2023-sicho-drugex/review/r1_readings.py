"""Wider menu of readings than 05 tries, from the two recount JSONs + the xlsx."""
import itertools, json, sys
import openpyxl

XLSX, DEFS, REC = sys.argv[1], sys.argv[2], sys.argv[3]
TARGETS = {("ChEMBL 27","LSTM RNN"):"sequence LSTM RNN", ("ChEMBL 31","GRU RNN"):"sequence GRU RNN"}
wb = openpyxl.load_workbook(XLSX, data_only=True); ws = wb["Values"]
rows = list(ws.iter_rows(values_only=True))
header = [str(c).strip() if c is not None else "" for c in rows[1]]
col = {n:i for i,n in enumerate(header)}
pub = {}
for row in rows[2:]:
    if row[0] is None: continue
    key = (str(row[col["dataset"]]).strip(), str(row[col["DrugEx version"]]).strip())
    if key not in TARGETS: continue
    pub["%s|%s|%s" % (str(row[col["Machine"]]).strip(), key[0], TARGETS[key])] = (
        float(row[col["validity"]]), float(row[col["uniqueness"]]))

d = json.load(open(DEFS)); r = json.load(open(REC))
cells = [c for c in pub if c in d]
cand = {}
for c in cells:
    D, R = d[c], r[c]
    n = D["n"]; valid_flag = R["valid_flag_over_n"]*n; parse = D["validity_parseable"]*n
    draw = D["uniqueness_distinct_raw_over_n"]*n; dcanon = D["distinct_canonical"]
    dvalid_raw = R["distinct_valid_smiles"]; uflag = R["unique_flag_over_n"]*n
    m = {
      "V:their_flag": valid_flag/n, "V:parseable": parse/n,
      "V:single_fragment": D["validity_single_fragment"],
      "V:parseable_over_distinct_raw": parse/draw,
      "V:valid_flag_over_distinct_raw": valid_flag/draw,
      "V:distinct_valid_raw_over_distinct_raw": dvalid_raw/draw,
      "U:their_flag": uflag/n, "U:distinct_raw_over_n": draw/n,
      "U:distinct_canon_over_n": dcanon/n,
      "U:distinct_canon_over_valid": dcanon/parse,
      "U:distinct_canon_over_valid_flag": dcanon/valid_flag,
      "U:distinct_valid_raw_over_valid_flag": dvalid_raw/valid_flag,
      "U:distinct_canon_over_distinct_raw": dcanon/draw,
      "U:distinct_valid_raw_over_distinct_raw": dvalid_raw/draw,
      "U:unique_flag_over_valid_flag": uflag/valid_flag,
      "U:distinct_canon_over_distinct_valid_raw": dcanon/dvalid_raw,
    }
    cand[c] = m

V = [k for k in next(iter(cand.values())) if k.startswith("V:")]
U = [k for k in next(iter(cand.values())) if k.startswith("U:")]
print("per-cell readings:")
for c in sorted(cells):
    print(" ", c, json.dumps({k: round(v,5) for k,v in cand[c].items()}, indent=None))
    print("   published", pub[c])
hits = []
for v,u in itertools.product(V,U):
    bad = [(c, round(cand[c][v],5), round(cand[c][u],5)) for c in cells
           if abs(cand[c][v]-pub[c][0]) > 0.01*pub[c][0] or abs(cand[c][u]-pub[c][1]) > 0.01*pub[c][1]]
    if not bad: hits.append((v,u))
    elif len(bad) <= 1: print("NEAR MISS (1 cell off):", v, u, bad)
print("pairs matching every cell of both models:", hits)
# uniqueness-only, per model
for u in U:
    for model in ("ChEMBL 27","ChEMBL 31"):
        cs = [c for c in cells if model in c]
        off = [c for c in cs if abs(cand[c][u]-pub[c][1]) > 0.01*pub[c][1]]
        if len(off) <= 1:
            print("uniqueness reading %-45s %s: %d/%d machines inside" % (u, model, len(cs)-len(off), len(cs)),
                  [(c.split('|')[0], round(cand[c][u],5), pub[c][1]) for c in cs])
