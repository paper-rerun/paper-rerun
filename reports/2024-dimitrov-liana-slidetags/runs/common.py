# Shared bits: paths, dataset map (notebook cell 6), authors' utils.py imported unchanged from sources/
import os, sys
R = '/mnt/e/Ciencia/noturno/2024-dimitrov-liana-slidetags'
DATA = os.path.join(R, 'data', 'slidetags')
RUNS = os.path.join(R, 'runs')
sys.path.insert(0, os.path.join(R, 'sources'))
d = {
     'SCP2167': 'humancortex',
     'SCP2169': 'HumanTonsil',
     'SCP2170': 'mouseembryo',
     'SCP2171': 'HumanMelanomaRNA',
     'SCP2176': 'HumanMelanomaMultiome'
     }
