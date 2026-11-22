import json, re, sys
from pathlib import Path

tex = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics-cego\arxiv-src\main.tex').read_text(encoding='utf-8', errors='replace').splitlines()

start = next(i for i, l in enumerate(tex) if 'tab:list}' in l and 'caption' in l)
end = next(i for i, l in enumerate(tex[start:], start) if l.strip().startswith('\\bottomrule'))
block = tex[start + 1:end]

PARAM = {
    '\\log_{10}T_{\\rm rh}/\\textrm{GeV}': 'log10_T_rh',
    '\\log_{10}r': 'log10_r',
    'n_t': 'n_t',
    '\\log_{10}A_{\\scriptscriptstyle\\rm BHB}': 'log10_A_bhb',
    '\\gamma_{\\scriptscriptstyle\\rm BHB}': 'gamma_bhb',
    '\\log_{10}A': 'log10_A',
    '\\log_{10}f_*/{\\rm Hz}': 'log10_f_star',
    '\\Delta': 'Delta',
    '\\log_{10}f_{\\rm min}/{\\rm Hz}': 'log10_f_min',
    '\\log_{10}f_{\\rm max}/{\\rm Hz}': 'log10_f_max',
    '\\log_{10}T_{\\rm *}/\\textrm{GeV}': 'log10_T_star',
    '\\log_{10}\\alpha_*': 'log10_alpha_star',
    '\\log_{10}H_*R_*': 'log10_HR',
    'a': 'a', 'b': 'b', 'c': 'c',
    '\\log_{10}G\\mu': 'log10_Gmu',
    '\\sqrt{\\kappa}': 'sqrt_kappa',
    '\\log_{10}P': 'log10_P',
    '\\log_{10} \\Delta N_{\\rm eff}': 'log10_dNeff',
}

BS = chr(92)


def clean(s):
    return s.strip().rstrip(BS).strip()


def parse_scalar(s):
    s = clean(s)
    if s in ('$...$', '...', '$---$', '---'):
        return None
    star = '^*' in s or '^{*}' in s
    s = s.replace('^*', '').replace('^{*}', '')
    s = s.strip('$').strip()
    m = re.match(r'^(-?[\d.]+)\s*' + BS + BS + r'pm\s*(-?[\d.]+)$', s)
    if m:
        return {'value': float(m.group(1)), 'sd': float(m.group(2)), 'boundary': star}
    m = re.match(r'^(-?[\d.]+)$', s)
    if m:
        return {'value': float(m.group(1)), 'boundary': star}
    raise ValueError('scalar? ' + repr(s))


def parse_ci(s):
    s = clean(s)
    if s in ('$...$', '...', '$---$', '---'):
        return None
    inner = re.search(BS + BS + r'left\[(.*?)' + BS + BS + r'right\]', s)
    if not inner:
        raise ValueError('ci? ' + repr(s))
    lo, hi = inner.group(1).split(',')

    def one(t):
        st = '^*' in t
        return float(t.replace('^*', '').strip()), st

    lov, star_lo = one(lo)
    hiv, star_hi = one(hi)
    return {'lo': lov, 'hi': hiv, 'lo_boundary': star_lo, 'hi_boundary': star_hi,
            'raw': inner.group(1).strip()}


rows = []
model = None
for raw in block:
    line = raw.strip()
    if not line or line.startswith('%'):
        continue
    m = re.search(BS + BS + r'textsc\{\(?([a-z' + BS + r'-]+)\)?\}', line)
    if '\\multicolumn{8}{c}' in line and m:
        model = m.group(1)
        continue
    if '\\multicolumn{8}' in line or line.startswith('\\toprule') or line.startswith('\\hline'):
        continue
    body = re.sub(BS + BS + BS + BS + r'.*$', '', line)
    cols = body.split('&')
    if len(cols) != 8:
        continue
    pname_tex = cols[0].strip().strip('$').strip()
    key = PARAM.get(pname_tex)
    if key is None:
        print('UNKNOWN PARAM ' + repr(pname_tex), file=sys.stderr)
        continue
    rows.append({
        'model': model, 'param': key, 'param_tex': pname_tex,
        'bayes_NP': parse_scalar(cols[1]), 'bayes_NPSMBHB': parse_scalar(cols[2]),
        'maxpost_NP': parse_scalar(cols[3]), 'maxpost_NPSMBHB': parse_scalar(cols[4]),
        'ci68_NP': parse_ci(cols[5]), 'ci68_NPSMBHB': parse_ci(cols[6]),
        'Kbound': parse_scalar(cols[7]),
    })

print(json.dumps(rows, indent=1))
print('# rows=%d models=%d' % (len(rows), len(set(r['model'] for r in rows))), file=sys.stderr)
