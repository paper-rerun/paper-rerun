#!/bin/bash
# Extract the 2022 checkpoint tars into runs/eval (cwd of the authors' script) and make the D11 renamed copies
set -e
W=/mnt/e/Ciencia/noturno/2022-takamoto-pdebench
mkdir -p $W/runs/eval; cd $W/runs/eval
for t in advection_FNO burgers_FNO DarcyFlow_FNO advection_Unet burgers_Unet DarcyFlow_Unet; do
  tar -tvf $W/data/ckpt/$t.tar
  tar -xf $W/data/ckpt/$t.tar --transform='s#.*/##'
done
for b in 0.01 0.1 1.0 10.0 100.0; do
  src=2D_DarcyFlow_beta${b}_Train_Unet_PF_1.pt; dst=2D_DarcyFlow_beta${b}_Train_Unet-PF-1.pt
  cp $src $dst; cmp $src $dst && echo "D11 copy ok $dst"
done
md5sum *.pt > $W/runs/ckpt_md5.txt; cat $W/runs/ckpt_md5.txt
