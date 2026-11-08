import os
import zipfile

SRC = r"E:\Ciencia\noturno\2023-yuksel-selformer-cego\downloads\archives\classification_models.zip"
DST = r"E:\Ciencia\noturno\2023-yuksel-selformer-cego\downloads\models"

os.makedirs(DST, exist_ok=True)
z = zipfile.ZipFile(SRC)
for info in z.infolist():
    name = info.filename
    if "__MACOSX" in name or name.endswith(".DS_Store"):
        continue
    # Skip optimizer states: 700 MB each and useless for inference
    if name.endswith("optimizer.pt"):
        continue
    if ".." in name or name.startswith("/") or name.startswith("\\"):
        print("SKIP suspicious path:", name)
        continue
    z.extract(info, DST)
    print(info.file_size, name)
