# List the structure of the published per-event samples file
import sys
import h5py
with h5py.File(sys.argv[1], "r") as samples_file:
    def show(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(name, obj.shape, obj.dtype, obj.dtype.names)
        else:
            print(name + "/", dict(obj.attrs))
    samples_file.visititems(show)
    print("root attrs", dict(samples_file.attrs))
