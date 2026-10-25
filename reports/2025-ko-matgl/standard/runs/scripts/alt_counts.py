"""Count claims within the pre-registered tolerance under each secondary definition (never enters the verdict)."""
import json, sys
claims = json.load(open("claims.json", encoding="utf-8"))["claims"]
r = json.load(open(sys.argv[1]))
E = ["energy_mae_meV_per_atom", "alt_b_energy_total_mae_over_mean_n", "alt_d_energy_unweighted_file_mean", "exploratory_molecule_centered_energy_mae_meV_per_atom"]
F = ["force_mae_eV_per_A", "alt_b_force_mean_of_per_conf_mae", "alt_c_force_vector_norm_per_atom", "alt_d_force_unweighted_file_mean"]
out = {}
for grouping in ["primary", "alt_gdb_grouping"]:
    for keyset in (E, F):
        for key in keyset:
            n = m = 0
            for c in claims:
                if (c["id"][0] == "E") != (keyset is E):
                    continue
                k = f"{c['model']}|{c['group_label_in_figure']}"
                src = r[grouping] if k in r[grouping] else r["primary"]
                v = src[k][key]
                n += 1
                m += abs(v - c["paper_value"]) <= c["tolerance"]["absolute"]
            out[f"{grouping}|{key}"] = f"{m}/{n}"
print(json.dumps(out, indent=1))
