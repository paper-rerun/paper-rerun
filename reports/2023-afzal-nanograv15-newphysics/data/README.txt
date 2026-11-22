What is here, and what is not.

Nothing in this folder is redistributed. The chains come from the authors' Zenodo deposit and
are fetched by hand:

  https://zenodo.org/records/8083620/files/chains.gz
  concept DOI 10.5281/zenodo.8010909, version DOI 10.5281/zenodo.8083620

  chains.gz    22,440,020,155 B
    md5    464a0c2f2645aec4bd72cbd9f1bfb4cf   (as published by Zenodo, and our copy matches)
    sha256 c9a6db2afdda38e0fc8f48f066fc56d1978505600f026f610ba9f5383a8a9d78
    (recorded by us, because Zenodo publishes only md5)

CC-BY-4.0. No login, no click-through, TLS verification on.

The archive holds chains/stochastic (the models of Table 4) and chains/deterministic (the
ultralight-dark-matter and substructure searches, which this run does not touch). We unpacked
only the stochastic branch.

The files are gzipped Python pickles. pickle.load executes whatever the file tells it to, so
every script here reads them through a restricted unpickler that allows only the three numpy
names needed to rebuild an array.

The article is the publisher's and is not here. Its numbers were read from the LaTeX source of
arXiv:2306.16219, fetched from https://arxiv.org/e-print/2306.16219, because the HTML rendering
prints every table cell twice and loses the bracket structure of the intervals.
