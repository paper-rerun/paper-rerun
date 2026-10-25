# Check that state.pt fills every parameter of the model built by load_model (it loads with strict=False)
import torch
import matgl
Dir = "/mnt/e/Ciencia/pipeline/2025-ko-matgl/data/weights/M3GNet-ANI-1x-Subset-PES"
State = torch.load(f"{Dir}/state.pt", map_location="cpu")
InitArgs = torch.load(f"{Dir}/model.pt", map_location="cpu")
print("model.pt keys:", {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "init_args"}) for k, v in InitArgs.items() if k != "model"})
print("model.pt model init_args:", InitArgs["model"]["init_args"] if isinstance(InitArgs.get("model"), dict) else type(InitArgs.get("model")))
Potential = matgl.load_model(Dir)
ModelKeys = set(Potential.state_dict().keys())
StateKeys = set(State.keys())
print("n model keys", len(ModelKeys), "n state keys", len(StateKeys))
print("missing in state:", sorted(ModelKeys - StateKeys))
print("unexpected in state:", sorted(StateKeys - ModelKeys))
Mismatch = [k for k in ModelKeys & StateKeys if Potential.state_dict()[k].shape != State[k].shape]
print("shape mismatch:", Mismatch)
Diff = max(float((Potential.state_dict()[k].float() - State[k].float()).abs().max()) for k in ModelKeys & StateKeys if State[k].numel())
print("max |loaded - state| over shared keys:", Diff)
print("data_mean", Potential.data_mean, "data_std", Potential.data_std, "element_refs", getattr(Potential, "element_refs", None) and Potential.element_refs.property_offset)
