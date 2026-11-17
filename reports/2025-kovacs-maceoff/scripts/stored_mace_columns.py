"""A3: the released test file already carries MACE_energy and MACE_forces.

Score those stored columns against the DFT reference the same way, per subset, so
they can be compared with Table S1 and the model that wrote them identified.
Pure text parsing, one pass, no model.
"""
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XYZ = os.path.join(ROOT, "data", "test_extract", "test_large_neut_all.xyz")

ctype_re = re.compile(r'config_type=(?:"([^"]*)"|(\S+))')
energy_re = re.compile(r'(?<!_)energy=(-?[\d.eE+]+)')
mace_e_re = re.compile(r'MACE_energy=(-?[\d.eE+]+)')

acc = {}
with open(XYZ) as fh:
    while True:
        line = fh.readline()
        if not line:
            break
        nat = int(line)
        com = fh.readline()
        mm = ctype_re.search(com); ct = mm.group(1) or mm.group(2)
        e_ref = float(energy_re.search(com).group(1))
        m = mace_e_re.search(com)
        e_mace = float(m.group(1)) if m else None
        f_ref = np.empty((nat, 3))
        f_mace = np.empty((nat, 3))
        has_mace_f = "MACE_forces" in com
        for i in range(nat):
            p = fh.readline().split()
            f_ref[i] = [float(x) for x in p[4:7]]
            if has_mace_f:
                f_mace[i] = [float(x) for x in p[7:10]]
        a = acc.setdefault(ct, [0, 0, 0.0, 0.0, 0, 0])
        a[0] += 1
        a[1] += nat
        if e_mace is not None:
            a[2] += abs(e_mace - e_ref) / nat
            a[4] += 1
        if has_mace_f:
            a[3] += np.abs(f_mace - f_ref).sum()
            a[5] += nat

print(f"{'subset':22s} {'n':>6s} {'n_E':>6s} {'E_mae':>8s} {'F_mae':>9s}")
for k, (n, nat, se, sf, ne, nf) in sorted(acc.items()):
    e = 1000 * se / ne if ne else float("nan")
    f = 1000 * sf / (3 * nf) if nf else float("nan")
    print(f"{k:22s} {n:6d} {ne:6d} {e:8.3f} {f:9.3f}")
