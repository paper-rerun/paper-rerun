import zipfile, tarfile, io
z = zipfile.ZipFile(r"E:\Ciencia\noturno\2023-antoniadis-epta-dr2\data\chains.zip")
for n in sorted(z.namelist()):
    if not n.endswith(".tar.gz"): continue
    data = io.BytesIO(z.read(n))
    t = tarfile.open(fileobj=data, mode="r:gz")
    members = [m.name for m in t.getmembers() if m.isfile()]
    print("==", n)
    print("   members:", members)
    for m in members:
        if m.endswith("pars.txt"):
            pars=[l.strip() for l in t.extractfile(m).read().decode().splitlines() if l.strip()]
            gw=[p for p in pars if not p[0].isdigit() and ("gw" in p or "crn" in p or "hd" in p)]
            print("   npars:", len(pars), " gw-ish:", gw[:4], "..." if len(gw)>4 else "", "n_gw:", len(gw))
