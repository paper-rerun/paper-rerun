# Orchestrates the whole run, restartable: skips any step whose output already exists.
# Per data file: (assemble sparse copy) -> authors' script for FNO and U-Net -> our diag pass -> (delete sparse copy)
import json, os, subprocess, time, sys
W = '/mnt/e/Ciencia/noturno/2022-takamoto-pdebench'
PY = W + '/env/.venv/bin/python'
SCRIPT = W + '/repo/pdebench/models/train_models_forward.py'
ENV = dict(os.environ, OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', OPENBLAS_NUM_THREADS='4',
           NUMEXPR_NUM_THREADS='4', MPLBACKEND='Agg', CUDA_VISIBLE_DEVICES='', PYTHONHASHSEED='0')
PREFIX = ['nice', '-n', '19', 'taskset', '-c', '8-11']
claims = json.load(open(W + '/claims.json'))['claims']
os.makedirs(W + '/runs/logs', exist_ok=True); os.makedirs(W + '/runs/preds', exist_ok=True)

def log(msg):
    print(time.strftime('%Y-%m-%dT%H:%M:%S'), msg, flush=True)

def wait_for(path):
    while not os.path.exists(path):
        log('waiting for ' + path); time.sleep(120)

def wait_mem(gb):
    while True:
        avail = int([l for l in open('/proc/meminfo') if l.startswith('MemAvailable')][0].split()[1]) / 1e6
        if avail >= gb:
            return
        log('waiting for memory, available %.1f GB' % avail); time.sleep(120)

# Groups: one per data file. beta4.0 advection is run on the full file and again on its sparse copy (D14 check)
groups = {}
for c in claims:
    f = c['conditions']['data_file']
    groups.setdefault(f, []).append(c)
order = [f for f in groups if f.startswith('2D')] + ['1D_Advection_Sols_beta4.0.hdf5', 'SPARSECHECK'] + \
        [f for f in groups if f.startswith('1D') and f != '1D_Advection_Sols_beta4.0.hdf5']
groups['SPARSECHECK'] = groups['1D_Advection_Sols_beta4.0.hdf5']

for g in order:
    cl = groups[g]
    fname = cl[0]['conditions']['data_file']
    pde = cl[0]['pde']
    sparse = g == 'SPARSECHECK' or (fname.startswith('1D') and fname != '1D_Advection_Sols_beta4.0.hdf5')
    ddir = W + ('/data/sparse/' if sparse else '/data/')
    suffix = '-sparse' if g == 'SPARSECHECK' else ''
    jobs = []
    for c in cl:
        model = 'FNO' if c['model'] == 'FNO' else 'Unet'
        tag = c['id'].replace('-nRMSE', '') + suffix
        ckpt = c['conditions']['checkpoint_loaded_as'].split(' ')[0]
        ist = 1 if pde == 'Darcy' else 10
        jobs.append(dict(tag=tag, model=model, ckpt=W + '/runs/eval/' + ckpt, ckname=ckpt, initial_step=ist,
                         rr=2 if pde == 'Darcy' else 4, rrt=1 if pde == 'Darcy' else 5,
                         pred_out=W + '/runs/preds/' + tag + '.npy'))
    diag_out = W + '/runs/diag_' + fname.replace('.hdf5', '') + suffix + '.json'
    todo = [j for j in jobs if not os.path.exists(W + '/runs/jobs/' + j['tag'] + '/DONE')]
    if not todo and os.path.exists(diag_out):
        log('skip group ' + g); continue
    # Data ready?
    if sparse:
        wait_for(W + '/data/sparse/' + fname + '.done')
        if g == 'SPARSECHECK':
            wait_for(W + '/data/' + fname + '.done')
        log('assemble ' + fname)
        subprocess.run(['nice', '-n', '19', 'bash', W + '/runs/assemble_sparse.sh', fname], check=True)
    else:
        wait_for(W + '/data/' + fname + '.done')
    cfg = {'Advection': 'config_Adv.yaml', 'Burgers': 'config_Bgs.yaml', 'Darcy': 'config_Darcy.yaml'}[pde]
    for j in todo:
        jd = W + '/runs/jobs/' + j['tag']; os.makedirs(jd, exist_ok=True)
        link = jd + '/' + j['ckname']
        if not os.path.lexists(link):
            os.symlink(j['ckpt'], link)
        args = ['+args=' + cfg, '++args.filename=' + fname, '++args.model_name=' + j['model'],
                '++args.if_training=False', '++args.data_path=' + ddir]
        if pde == 'Darcy':
            args += ['++args.initial_step=1', '++args.t_train=2', '++args.reduced_resolution=2', '++args.reduced_resolution_t=1']
            if j['model'] == 'Unet':
                args += ['++args.ar_mode=True', '++args.pushforward=True', '++args.unroll_step=1']
        wait_mem(12 if fname.startswith('1D') else 5)
        cmd = PREFIX + [PY, SCRIPT] + args
        log('run ' + j['tag'] + ' : ' + ' '.join(cmd))
        t0 = time.time()
        with open(W + '/runs/logs/' + j['tag'] + '.log', 'w') as lf:
            lf.write('cmd: ' + ' '.join(cmd) + '\ncwd: ' + jd + '\n'); lf.flush()
            rc = subprocess.run(cmd, cwd=jd, env=ENV, stdout=lf, stderr=subprocess.STDOUT).returncode
            lf.write('\nreturncode %d wall %.1f s\n' % (rc, time.time() - t0))
        if rc != 0:
            log('FAILED ' + j['tag']); sys.exit(1)
        open(jd + '/DONE', 'w').write('%.1f\n' % (time.time() - t0))
        log('done ' + j['tag'] + ' %.0f s' % (time.time() - t0))
    if not os.path.exists(diag_out):
        wait_mem(12 if fname.startswith('1D') else 5)
        dj = [{k: j[k] for k in ('tag', 'model', 'ckpt', 'initial_step', 'rr', 'rrt', 'pred_out')} for j in jobs]
        cmd = PREFIX + [PY, W + '/runs/diag.py', ddir, fname, json.dumps(dj), diag_out, W + '/runs/metrics_268ba5e.py']
        log('diag ' + g)
        with open(W + '/runs/logs/diag_' + fname.replace('.hdf5', '') + suffix + '.log', 'w') as lf:
            rc = subprocess.run(cmd, cwd=W + '/runs', env=ENV, stdout=lf, stderr=subprocess.STDOUT).returncode
        if rc != 0:
            log('DIAG FAILED ' + g); sys.exit(1)
    if sparse:
        os.remove(W + '/data/sparse/' + fname); log('removed assembled ' + fname)
log('PIPELINE DONE')
