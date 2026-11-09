# Print stored metadata of the HyperModel core (runtime info, if any)
from la_forge import core
c = core.Core(corepath="/mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/repo/tutorials/presampled_cores/curn_hd.core")
for attribute in ["runtime_info", "label", "fancy_par_names"]:
	value = getattr(c, attribute, None)
	print(attribute, ":", (str(value)[:3000] if value is not None else None))
