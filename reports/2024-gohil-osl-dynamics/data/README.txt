What is here, and what is not.

Nothing in this folder is redistributed. The data and the trained models come from the
authors' OSF deposit, which the paper's data-availability statement names, and are fetched by
hand from:

  https://osf.io/by2tc/

  notts_meguk_giles.zip                  684,320,829 B
    sha256 c6bb9b81844e156af410071d96f53d6e460bc5fa9e0347ee63fc5ab691857463
    65 subjects: networks/subjectNN.npy (source-reconstructed parcel time courses, 250 Hz,
    38 Giles parcels), bursts/, demographics.csv. This is the CTF Rest dataset used in
    Figure 4.
  trained_tde_hmm.zip                        667,001 B
    sha256 b4065eb770b3d8097cf1e3ae9b0185d1840b0e1ee7d9e191305b3bdaf4c34c2d
    = tde_hmm_notts_meguk_giles, https://osf.io/download/zemj4/
  tde_hmm_notts_meguk_glasser.zip          1,362,440 B
    sha256 2bdca6fe88fa8447a4cf2c56989f4afb8fd6018b795db3a18b0ca989b04fa786
    https://osf.io/download/fmz4c/
  ae_hmm_notts_meguk_glasser.zip             199,141 B
    sha256 7481ab647570784e24fcecf5de6f1a7ffd1817f0272bd3cf87f08287af933cb1
    https://osf.io/download/m846x/
  tde_dynemo_20_runs.zip                   2,504,778 B
    sha256 e3016e870de0467c5a8063c9f753f8de7d4fae93bf1c23a7140666d18614c91d
  inf_tde_hmm_5subj.zip                   11,242,813 B
    sha256 0726ca8407e90de62c8c152a9bdf78ee866201896a1e6bd23c0953535f46ce66

No login, no click-through, TLS verification on.

The parcellation file is not here either, and it is not pinned anywhere: osl-dynamics fetches
atlas-Giles_nparc-38_space-MNI_res-8x8x8.nii.gz from OHBA-analysis/osl-files at run time, and
its own fetcher re-downloads a file whenever the checksum changes. Anyone repeating this gets
whatever is current.

The article is the publisher's and is not here. Its text was read from the Europe PMC XML of
PMC10945565, because eLife's own HTML returns a 232-byte bot challenge. Figure 4 was fetched
from the eLife IIIF endpoint for reading only and is not redistributed.
