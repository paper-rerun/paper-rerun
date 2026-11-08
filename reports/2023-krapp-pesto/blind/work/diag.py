import sys, os
sys.path.insert(0,'scripts')
import numpy as np
from pesto_rerun import build_assembly, fetch_assembly, MAX_NUM_ATOMS
sys.path.insert(0,'repo')
from src.structure_io import read_pdb
from src.structure import clean_structure, tag_hetatm_chains, split_by_chain, filter_non_atomic_subunits, remove_duplicate_tagged_subunits
for pid in ['1FSS','4DX0']:
    fp=fetch_assembly(pid,1)
    s=read_pdb(fp)
    print(pid,'raw atoms',s['xyz'].shape[0],'limit',MAX_NUM_ATOMS,'-> skipped' if s['xyz'].shape[0]>=MAX_NUM_ATOMS else '-> kept')
    c=clean_structure(s); c=tag_hetatm_chains(c); su=split_by_chain(c); su=filter_non_atomic_subunits(su)
    print('   chains after cleaning:', {k:v['xyz'].shape[0] for k,v in su.items()})
    e,info=build_assembly(fp)
    print('   entries:', {k:(v[0]['xyz'].shape[0], int(v[1].sum()), v[1].shape[0]) for k,v in e.items()}, info)
