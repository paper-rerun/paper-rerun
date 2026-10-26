"""Find where weaver-core 0.5.3 diverges from 0.4.17 with the released ParT_full.pt (CPU, first 512 jets of HToBB_100.root)

Run with each env's python:
  python diag_weaver053.py dump <tag> <out_dir>          inputs + softmax from this weaver's loader and model
  python diag_weaver053.py feed <tag> <other.npz> <out_dir>  this weaver's model on the other weaver's inputs
"""
import os
import sys

import numpy as np
import torch

HERE = '/mnt/e/Ciencia/noturno/2022-qu-particle-transformer'
FILE = f'{HERE}/data/JetClass/test_20M/HToBB_100.root'
YAML = f'{HERE}/repo/data/JetClass/JetClass_full.yaml'
NETWORK = f'{HERE}/repo/networks/example_ParticleTransformer.py'
CKPT = f'{HERE}/data/weights/ParT_full.pt'


def load_first_batch():
    import weaver
    from weaver.utils.dataset import SimpleIterDataset
    version = getattr(weaver, '__version__', '')
    if os.path.isdir(os.path.join(os.path.dirname(weaver.__file__), 'nn', 'model')) and 'split_num' in open(
            os.path.join(os.path.dirname(weaver.__file__), 'utils', 'dataset.py')).read():
        load_range = ((0, 1), 1, 1)
    else:
        load_range = ((0, 1), 1)
    dataset = SimpleIterDataset({'HToBB': [FILE]}, YAML, for_training=False, load_range_and_fraction=load_range,
                                fetch_by_files=True, fetch_step=1, name='diag')
    loader = torch.utils.data.DataLoader(dataset, num_workers=0, batch_size=512, drop_last=False)
    X, y, Z = next(iter(loader))
    config = dataset.config
    inputs = {k: X[k].numpy() for k in config.input_names}
    jet_pt = np.asarray(Z['jet_pt'])
    return config, inputs, jet_pt, version


def build_model(config):
    import importlib.util
    spec = importlib.util.spec_from_file_location('netcfg', NETWORK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model, _ = module.get_model(config)
    model.load_state_dict(torch.load(CKPT, map_location='cpu'))
    model.eval()
    return model


def run_model(model, config, inputs):
    with torch.no_grad():
        logits = model(*[torch.from_numpy(inputs[k]) for k in config.input_names])
        return torch.softmax(logits.float(), dim=1).numpy()


def main():
    mode, tag = sys.argv[1], sys.argv[2]
    if mode == 'dump':
        out_dir = sys.argv[3]
        config, inputs, jet_pt, version = load_first_batch()
        model = build_model(config)
        scores = run_model(model, config, inputs)
        np.savez(f'{out_dir}/diag_{tag}.npz', jet_pt=jet_pt, scores=scores, **inputs)
        print(tag, 'input names', list(config.input_names), 'shapes', {k: v.shape for k, v in inputs.items()})
        print(tag, 'mean softmax Hbb (true class) %.4f, accuracy %.4f' % (scores[:, 1].mean(), np.mean(scores.argmax(1) == 1)))
    else:
        other, out_dir = sys.argv[3], sys.argv[4]
        data = np.load(other)
        config, _, _, _ = load_first_batch()
        model = build_model(config)
        inputs = {k: data[k] for k in config.input_names}
        scores = run_model(model, config, inputs)
        np.save(f'{out_dir}/diag_feed_{tag}_on_{os.path.basename(other)}.npy', scores)
        print(tag, 'model on', os.path.basename(other), 'inputs: accuracy %.4f, max |score - other model score| %.3g' % (
            np.mean(scores.argmax(1) == 1), np.abs(scores - data['scores']).max()))


if __name__ == '__main__':
    main()
