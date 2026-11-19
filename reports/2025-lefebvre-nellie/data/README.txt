What is here, and what is not.

Nothing. The benchmark is not data someone deposited, it is data the authors' own code
writes, so there is nothing to archive: run their generator and you get it back.

  git clone https://github.com/aelefebv/nellie-supplemental
  cd nellie-supplemental && git checkout 7a639bc
  python comparisons/simulations/multi_grid/multi_grid.py

That writes no_noise.ome.tif plus thirteen gaussian_std_<n>.ome.tif files, 9.9 GB in all,
three independent noise draws per file. It sets no RNG seed, so the volumes are not the
ones behind the figure and are not the ones we ran either, which is finding 5 of the
report. The scripts in ../scripts/ expect them under repo/nellie-supplemental/outputs/.

The published numbers we compare against are in the article's Source Data: Supplementary
Data 16, the Multigrid_F1_lv5_*.txt and IoU_Multigrid_F1_lv5_*.txt files. That file is the
publisher's and is not copied here. It is on the article page at Nature Methods, under
Supplementary information; what we read was 41592_025_02612_7_MOESM16_ESM.zip, 13,768
bytes, md5 a7002f298038b848537901f62005d553.

Nellie itself is on PyPI, and ../env/requirements.freeze.txt is what we ran: nellie 0.4.1
with scikit-image 0.22.0 and scipy 1.12.0, which is not what the supplemental's own
requirements.txt pins. That contradiction is also finding 5.
