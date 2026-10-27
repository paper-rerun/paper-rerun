#!/bin/bash
# Second try at the 285 missing AFDB members (same sequential downloader, v6 saved under the v4 name)
# Files already on disk are skipped when their size matches sizes.tsv
H=/mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/runs/afdb_download
cd /tmp
echo "start $(date -u +%FT%TZ)"
nice -n 19 python3 -I $H/fetch_afdb.py $H/aria_list.txt $H/sizes.tsv
echo "end $(date -u +%FT%TZ)"
# Size check of every file listed in sizes.tsv against what is on disk
python3 -I -c "
import os, sys
rows = [r.rstrip('\n').split('\t') for r in open(sys.argv[1])]
bad = [r[0] for r in rows if not os.path.exists(r[0]) or os.path.getsize(r[0]) != int(r[1])]
print('sizes.tsv rows', len(rows), 'size mismatches', len(bad))
for b in bad: print('MISMATCH', b)
" $H/sizes.tsv
find /mnt/e/Ciencia/noturno/2026-gilchrist-foldmason/data/afdb_clusters -name '*.pdb' | wc -l
