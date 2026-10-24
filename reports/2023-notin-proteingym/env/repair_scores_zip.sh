#!/bin/bash
# The power cut left bad bytes near the end of the first partial download (190,179,514 B).
# Re-fetch the byte range of the one entry that fails CRC (D7PM05_CLYGR_Somermeyer_2022.csv) and patch it in place
set -e
W=/mnt/e/Ciencia/meio/2023-notin-proteingym
Z=$W/sources/zero_shot_substitutions_scores.zip
URL=https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/zero_shot_substitutions_scores.zip
START=183000000
END=205000000
curl -sS -r $START-$END -o $W/sources/range.bin $URL
ls -l $W/sources/range.bin
cmp -l $W/sources/range.bin <(tail -c +$((START + 1)) $Z | head -c $((END - START + 1))) | wc -l | xargs echo "differing bytes in range:"
dd if=$W/sources/range.bin of=$Z bs=1M seek=$START oflag=seek_bytes conv=notrunc status=none
rm $W/sources/range.bin
unzip -tq $Z
