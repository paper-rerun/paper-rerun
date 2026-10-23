"""Run each Mamba CUDA kernel on its own so a failure points to the kernel, not to the next cuBLAS call"""
import torch
torch.manual_seed(0)
Device = "cuda:0"
for DataType in (torch.float32, torch.float16):
	print("dtype", DataType)
	try:
		from causal_conv1d import causal_conv1d_fn
		X = torch.randn(2, 64, 512, device=Device, dtype=DataType)
		W = torch.randn(64, 4, device=Device, dtype=DataType)
		Y = causal_conv1d_fn(X, W, None, activation="silu"); torch.cuda.synchronize()
		print("  causal_conv1d ok", float(Y.float().abs().mean()))
	except Exception as Error:
		print("  causal_conv1d FAIL", repr(Error)[:300])
	try:
		from mamba_ssm.ops.selective_scan_interface import selective_scan_fn
		B, D, L, N = 2, 64, 512, 16
		U = torch.randn(B, D, L, device=Device, dtype=DataType)
		Delta = torch.rand(B, D, L, device=Device, dtype=DataType)
		A = -torch.rand(D, N, device=Device)
		Bm = torch.randn(B, N, L, device=Device, dtype=DataType)
		Cm = torch.randn(B, N, L, device=Device, dtype=DataType)
		Y = selective_scan_fn(U, Delta, A, Bm, Cm, None, None, None, delta_softplus=True); torch.cuda.synchronize()
		print("  selective_scan ok", float(Y.float().abs().mean()))
	except Exception as Error:
		print("  selective_scan FAIL", repr(Error)[:300])
