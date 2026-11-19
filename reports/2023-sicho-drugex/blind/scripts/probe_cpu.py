import sys, torch
from drugex.data.corpus.vocabulary import VocSmiles
from drugex.training.generators import SequenceRNN

voc_path = sys.argv[1]
voc = VocSmiles.fromFile(voc_path, False, max_len=100)
print("voc size", voc.size, "max_len", voc.max_len)
try:
    m = SequenceRNN(voc, is_lstm=True, device=torch.device('cpu'))
    print("constructed OK, device =", m.device)
except Exception as e:
    print("CONSTRUCTION FAILED:", type(e).__name__, e)
