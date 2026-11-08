import sys, zipfile, re
import xml.etree.ElementTree as ET

def strip(tag): return tag.split('}')[-1]

def read(path, sheet_file):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root:
            ss.append(''.join(t.text or '' for t in si.iter() if strip(t.tag)=='t'))
    rows = []
    root = ET.fromstring(z.read(sheet_file))
    for row in root.iter():
        if strip(row.tag) != 'row': continue
        vals = {}
        for c in row:
            if strip(c.tag)!='c': continue
            ref = c.get('r'); col = re.match(r'([A-Z]+)', ref).group(1)
            t = c.get('t'); v = None
            for ch in c:
                if strip(ch.tag)=='v': v = ch.text
                elif strip(ch.tag)=='is': v = ''.join(x.text or '' for x in ch.iter() if strip(x.tag)=='t')
            if t=='s' and v is not None: v = ss[int(v)]
            vals[col]=v
        rows.append(vals)
    return rows

if __name__ == '__main__':
    rows = read(sys.argv[1], sys.argv[2])
    print('nrows', len(rows))
    for r in rows[:6]: print(r)
    print('...')
    for r in rows[-3:]: print(r)
