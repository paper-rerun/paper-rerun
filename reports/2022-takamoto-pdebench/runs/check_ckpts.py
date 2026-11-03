# Check the D2/D6 shapes of every checkpoint before running (fc0 / first conv in-channels, epoch)
import json, sys, torch
claims = json.load(open(sys.argv[1]))['claims']
out = {}
for c in claims:
    name = c['conditions']['checkpoint_loaded_as'].split(' ')[0]
    ck = torch.load('runs/eval/' + name, map_location='cpu')
    sd = ck['model_state_dict']
    if 'fc0.weight' in sd:
        key = 'fc0.weight'
    else:
        key = [k for k in sd if k.endswith('enc1conv1.weight')][0]
    shape = tuple(sd[key].shape)
    nparams = sum(v.numel() for v in sd.values())
    out[c['id']] = {'file': name, 'key': key, 'shape': shape, 'epoch': ck.get('epoch'), 'loss': float(ck.get('loss')) if ck.get('loss') is not None else None, 'n_params': nparams}
    print(c['id'], name, key, shape, 'epoch', ck.get('epoch'), 'params', nparams)
expected = {('FNO', '1D'): (20, 11), ('FNO', '2D'): (20, 3), ('U-Net', '1D'): (32, 10, 3), ('U-Net', '2D'): (32, 1, 3, 3)}
bad = 0
for c in claims:
    dim = '2D' if c['pde'] == 'Darcy' else '1D'
    if out[c['id']]['shape'] != expected[(c['model'], dim)]:
        print('UNEXPECTED SHAPE', c['id']); bad += 1
json.dump(out, open('runs/ckpt_check.json', 'w'), indent=1)
print('bad', bad)
