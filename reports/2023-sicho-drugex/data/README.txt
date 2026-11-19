What is here, and what is not.

chembl27/ and chembl31/ are the two pretrained models, unpacked from Zenodo. Both MIT, both
anonymous download, neither redistributed here:

  ChEMBL 27 LSTM RNN  10.5281/zenodo.7096837
    DrugEx_v2_PT_ChEMBL27.zip, 20,663,962 B, md5 ed6ebd972e530a108e16ed4646b2a38a
  ChEMBL 31 GRU RNN   10.5281/zenodo.7550739
    DrugEx_v2_GRU_PT_ChEMBL31.zip, 17,380,798 B, md5 7fe6693e865811a86b0d2140c6bf19cf

The ChEMBL 27 archive says in its own README that the model is DrugEx version 2; the ChEMBL 31
one says version 3.3.3. Both were sampled with the v3.4.9-dev code of this paper, because that
is the code the paper releases.

downloads/ holds the two deposited files of 10.5281/zenodo.7928362, CC BY 4.0, which is where
the published numbers live:

  DrugEx_pretrained_models_sampling_time.xlsx
    198,010 B, sha256 027e7ee2c9b9a80b9e8d33ea383b6b08f07facbeef2e4203fdf997d2089f1b0d
    Table S4 itself, plus one row per model per machine over six GPUs.
  DrugEx_pretrained_models_sampled_molecules.tsv.xz
    78,903,544 B, sha256 71751ae7408fdd283b9e76f4fd7c235673e76eba349c333c2b8832c8496be225
    496 MB unpacked, 2,240,000 molecules with the authors' Valid, Unique and Novel flag on
    each. Every script here streams it and never unpacks it to disk.

There is no benchmark input to fetch: the models sample from scratch. The article is the
publisher's and is not here either.
