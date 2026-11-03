# Our own scoring pass (diagnostics, does not decide the verdict).
# Loads the test split once with the authors' loader, reruns the same rollout as metrics() at b5b646f,
# saves the predictions and scores them three ways:
#   P  = metric_func at b5b646f (must equal the authors' pickle)
#   V1 = metric_func at 268ba5e (input slots excluded)
#   V2 = Eq. 4 of the supplement taken literally: sqrt of each per-sample, per-step ratio ||e||/||u||
import sys, json, importlib.util, numpy as np, torch
from pdebench.models.fno.utils import FNODatasetSingle
from pdebench.models.fno.fno import FNO1d, FNO2d
from pdebench.models.unet.unet import UNet1d, UNet2d
from pdebench.models.metrics import metric_func as metric_b5b646f

spec = importlib.util.spec_from_file_location('m268', sys.argv[5])
m268 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m268)

data_dir, filename, jobs_json, out_json = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
jobs = json.loads(jobs_json)  # list of {tag, model, ckpt, initial_step, rr, rrt}
first = jobs[0]
ds = FNODatasetSingle(filename, initial_step=first['initial_step'], saved_folder=data_dir,
                      reduced_resolution=first['rr'], reduced_resolution_t=first['rrt'], reduced_batch=1, if_test=True)
loader = torch.utils.data.DataLoader(ds, batch_size=50, shuffle=False, num_workers=0)
print('test samples', len(ds), 'shape', tuple(ds.data.shape), flush=True)

def v2_nrmse(pred, target):
    # Same layout handling as metric_func, but sqrt over each per-sample per-step ratio
    nd = target.dim()
    perm = [0, nd - 1] + list(range(1, nd - 1))
    p = pred.permute(perm); t = target.permute(perm)
    nb, nc, nt = t.shape[0], t.shape[1], t.shape[-1]
    e = torch.sqrt(torch.mean((p.reshape(nb, nc, -1, nt) - t.reshape(nb, nc, -1, nt)) ** 2, dim=2))
    n = torch.sqrt(torch.mean(t.reshape(nb, nc, -1, nt) ** 2, dim=2))
    r = torch.sqrt(e / n)
    return r.mean(dim=0)  # (nc, nt)

results = {}
for job in jobs:
    ist = job['initial_step']
    two_d = ds.data.dim() == 5
    if job['model'] == 'FNO':
        model = (FNO2d(num_channels=1, width=20, modes1=12, modes2=12, initial_step=ist) if two_d
                 else FNO1d(num_channels=1, width=20, modes=12, initial_step=ist))
    else:
        model = UNet2d(1 * ist, 1) if two_d else UNet1d(1 * ist, 1)
    ck = torch.load(job['ckpt'], map_location='cpu')
    model.load_state_dict(ck['model_state_dict']); model.eval()
    preds = []; acc = {'P': [], 'V1': [], 'V2_all': [], 'V2_pred': []}
    with torch.no_grad():
        for xx, yy, grid in loader:
            pred = yy[..., :ist, :]
            inp_shape = list(xx.shape)[:-2] + [-1]
            for t in range(ist, yy.shape[-2]):
                inp = xx.reshape(inp_shape)
                if job['model'] == 'FNO':
                    im = model(inp, grid)
                else:
                    temp_shape = [0, -1] + [i for i in range(1, len(inp.shape) - 1)]
                    inp = inp.permute(temp_shape)
                    temp_shape = [0] + [i for i in range(2, len(inp.shape))] + [1]
                    im = model(inp).permute(temp_shape).unsqueeze(-2)
                pred = torch.cat((pred, im), -2)
                xx = torch.cat((xx[..., 1:, :], im), dim=-2)
            preds.append(pred.numpy().astype(np.float32))
            acc['P'].append([float(v) for v in metric_b5b646f(pred, yy, if_mean=True)[:5]] +
                            [float(v) for v in metric_b5b646f(pred, yy, if_mean=True)[5]])
            r = m268.metric_func(pred, yy, if_mean=True, initial_step=ist)
            acc['V1'].append([float(v) for v in r[:5]] + [float(v) for v in r[5]])
            v2 = v2_nrmse(pred, yy)
            acc['V2_all'].append(float(v2.mean()))
            acc['V2_pred'].append(float(v2[:, ist:].mean()))
    preds = np.concatenate(preds)
    np.save(job['pred_out'], preds)
    names = ['RMSE', 'nRMSE', 'cRMSE', 'max', 'bRMSE', 'fRMSE_low', 'fRMSE_mid', 'fRMSE_high']
    res = {'P': dict(zip(names, np.mean(acc['P'], axis=0).tolist())),
           'V1': dict(zip(names, np.mean(acc['V1'], axis=0).tolist())),
           'V2_all_slots': float(np.mean(acc['V2_all'])), 'V2_pred_slots': float(np.mean(acc['V2_pred'])),
           'n_test': int(preds.shape[0]), 'pred_shape': list(preds.shape), 'torch': torch.__version__}
    results[job['tag']] = res
    print(job['tag'], json.dumps(res), flush=True)
json.dump(results, open(out_json, 'w'), indent=1)
