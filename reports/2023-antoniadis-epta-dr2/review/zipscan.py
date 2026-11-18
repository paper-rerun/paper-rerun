import zipfile, tarfile, io, sys
z = zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
names = z.namelist()
print(len(names), "entries")
for n in names: print(" ", n, z.getinfo(n).file_size)
