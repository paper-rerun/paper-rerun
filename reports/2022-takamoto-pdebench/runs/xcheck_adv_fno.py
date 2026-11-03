# Diagnostic for the Advection beta=1.0 FNO miss: score each of the four 2022 Advection FNO checkpoints
# on each of the four Advection test sets (same rollout and metric_func as the authors at b5b646f).
# Test sets are read straight from the downloaded head pieces (tensor contiguous from byte 2048);
# the reader is first checked against the authors' loader on the full beta4.0 file.
import json, numpy as np, torch, h5py
from pdebench.models.fno.utils import FNODatasetSingle
from pdebench.models.fno.fno import FNO1d
from pdebench.models.metrics import metric_func
W = '/mnt/e/Ciencia/noturno/2022-takamoto-pdebench'
betas = ['0.1', '0.4', '1.0', '4.0']

def read_head(beta):
    raw = np.fromfile(W + '/data/sparse/1D_Advection_Sols_beta%s.hdf5.head' % beta, dtype='<f4', offset=2048, count=1000 * 201 * 1024)
    a = raw.reshape(1000, 201, 1024)[:, ::5, ::4]
    return torch.tensor(np.ascontiguousarray(np.transpose(a, (0, 2, 1))[..., None]))

ref = FNODatasetSingle('1D_Advection_Sols_beta4.0.hdf5', initial_step=10, saved_folder=W + '/data/', reduced_resolution=4, reduced_resolution_t=5, if_test=True)
mine = read_head('4.0')
print('reader equals authors loader on beta4.0:', bool(torch.equal(ref.data, mine)), flush=True)
grid = ref.grid
with h5py.File(W + '/data/1D_Advection_Sols_beta4.0.hdf5', 'r') as f:
    print('beta4.0 file t-coordinate[::5][:3]', np.array(f['t-coordinate'])[::5][:3])
out = {}
for db in betas:
    data = read_head(db)
    for mb in betas:
        model = FNO1d(num_channels=1, width=20, modes=12, initial_step=10)
        model.load_state_dict(torch.load(W + '/runs/eval/1D_Advection_Sols_beta%s_FNO.pt' % mb, map_location='cpu')['model_state_dict']); model.eval()
        acc = []
        with torch.no_grad():
            for i in range(0, 1000, 50):
                yy = data[i:i + 50]; xx = yy[..., :10, :]; g = grid.unsqueeze(0).repeat(yy.shape[0], 1, 1)
                pred = yy[..., :10, :]
                for t in range(10, yy.shape[-2]):
                    im = model(xx.reshape(list(xx.shape)[:-2] + [-1]), g)
                    pred = torch.cat((pred, im), -2); xx = torch.cat((xx[..., 1:, :], im), dim=-2)
                acc.append(float(metric_func(pred, yy, if_mean=True)[1]))
        out['ckpt%s_on_data%s' % (mb, db)] = float(np.mean(acc))
        print('FNO ckpt beta', mb, 'on test data beta', db, 'nRMSE %.5g' % np.mean(acc), flush=True)
json.dump(out, open(W + '/runs/xcheck_adv_fno.json', 'w'), indent=1)
