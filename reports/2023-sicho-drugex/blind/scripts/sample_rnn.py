"""Sample raw SMILES from a released DrugEx RNN checkpoint on CPU.

Writes one raw sampled string per line (exactly num_samples lines), no filtering.
Everything downstream (validity, uniqueness) is computed by score_sample.py from this file.
"""
import argparse, os, sys, time, json
import torch

ap = argparse.ArgumentParser()
ap.add_argument('--pkg', required=True)
ap.add_argument('--vocab', required=True)
ap.add_argument('--arch', required=True, choices=['lstm', 'gru'])
ap.add_argument('--num', type=int, required=True)
ap.add_argument('--batch-size', type=int, default=600)
ap.add_argument('--seed', type=int, default=None)
ap.add_argument('--threads', type=int, default=4)
ap.add_argument('--out', required=True)
a = ap.parse_args()

import drugex  # sets torch.set_num_threads(1) at import, so override after
from drugex.data.corpus.vocabulary import VocSmiles
from drugex.training.generators import SequenceRNN

torch.set_num_threads(a.threads)

# v3.4.4 (and v3.4.8) hard-code 'cuda:{gpus[0]}' in SequenceRNN.attachToGPUs, which the base
# class calls with gpus=(-1,) on a CPU-only host. Keep the model on the CPU instead
_orig = SequenceRNN.attachToGPUs
def _cpu_safe_attach(self, gpus):
    if self.device is not None and self.device.type == 'cpu':
        self.gpus = (-1,)
        self.to(self.device)
        return
    return _orig(self, gpus)
SequenceRNN.attachToGPUs = _cpu_safe_attach

if a.seed is not None:
    torch.manual_seed(a.seed)

voc = VocSmiles.fromFile(a.vocab, False, max_len=100)
model = SequenceRNN(voc, is_lstm=(a.arch == 'lstm'), device=torch.device('cpu'))
model.loadStatesFromFile(a.pkg)
model.eval()

t0 = time.time()
written = 0
with open(a.out, 'w', encoding='utf-8', newline='\n') as fh, torch.no_grad():
    while written < a.num:
        n = min(a.batch_size, a.num - written) if a.num - written < a.batch_size else a.batch_size
        smiles = model.sample(a.batch_size)
        for s in smiles:
            if written >= a.num:
                break
            fh.write(s.replace('\t', ' ').replace('\n', ' ') + '\n')
            written += 1
        if written % 12000 < a.batch_size:
            el = time.time() - t0
            print(f'{written}/{a.num} {el:.0f}s eta {el / max(written,1) * (a.num - written):.0f}s', flush=True)
el = time.time() - t0
try:
    import psutil
    rss_mb = round(psutil.Process().memory_info().peak_wset / 2**20, 1)
except Exception:
    rss_mb = None
meta = dict(peak_rss_mb=rss_mb, pkg=a.pkg, vocab=a.vocab, arch=a.arch, num=a.num, batch_size=a.batch_size,
            seed=a.seed, threads=a.threads, voc_size=voc.size, max_len=voc.max_len,
            seconds=round(el, 2), ms_per_mol=round(el * 1000 / a.num, 4),
            drugex=drugex.about.VERSION, torch=torch.__version__)
print(json.dumps(meta))
with open(a.out + '.meta.json', 'w') as fh:
    json.dump(meta, fh, indent=2)
