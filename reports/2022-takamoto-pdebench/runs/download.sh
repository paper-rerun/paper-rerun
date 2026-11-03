#!/bin/bash
# Restartable serial download from DaRUS. Full files: md5 against server metadata.
# Sparse 1D files (claims D14): header + first 1000 samples (bytes 0-823298047) + last 6264 B, zeros in between
D=/mnt/e/Ciencia/noturno/2022-takamoto-pdebench/data
cd $D; mkdir -p ckpt sparse
HEAD_END=823298047; TAIL=6264
while IFS=$'\t' read -r id path size md5 mode; do
  [ -f "$path.done" ] && { echo "skip $path"; continue; }
  url="https://darus.uni-stuttgart.de/api/access/datafile/$id"
  echo "$(date -Is) start $path ($mode)"
  if [ "$mode" = full ]; then
    for try in 1 2 3 4 5 6 7 8 9 10; do
      have=$(stat -c %s "$path.part" 2>/dev/null || echo 0)
      [ "$have" -ge "$size" ] && break
      nice -n 19 curl -sS -L --fail -C - -o "$path.part" "$url" || { echo "curl err try $try"; sleep 20; }
    done
    have=$(stat -c %s "$path.part"); [ "$have" = "$size" ] || { echo "SIZE MISMATCH $path $have != $size"; exit 1; }
    got=$(nice -n 19 md5sum "$path.part" | cut -d' ' -f1)
    [ "$got" = "$md5" ] || { echo "MD5 MISMATCH $path $got"; exit 1; }
    mv "$path.part" "$path"; echo "$size $got server=$md5" > "$path.done"
  else
    h="$path.head"; t="$path.tail"
    full=$(basename "$path")
    if [ -f "$full.done" ]; then
      # Build the sparse copy from the verified full file, same byte ranges
      dd if="$full" of="$h" bs=1M count=$(( (HEAD_END+1)/1048576 )) status=none
      dd if="$full" of="$h" bs=1 skip=$(( (HEAD_END+1)/1048576*1048576 )) seek=$(( (HEAD_END+1)/1048576*1048576 )) count=$(( (HEAD_END+1)%1048576 )) conv=notrunc status=none
      tail -c $TAIL "$full" > "$t"
      printf 'content-range: bytes %d-%d/%d
' $((size-TAIL)) $((size-1)) $(stat -c %s "$full") > "$path.tailhdr"
    fi
    for try in 1 2 3 4 5 6 7 8 9 10; do
      have=$(stat -c %s "$h" 2>/dev/null || echo 0)
      [ "$have" -gt "$HEAD_END" ] && break
      nice -n 19 curl -sS -L --fail -r "$have-$HEAD_END" "$url" >> "$h" || { echo "curl err try $try"; sleep 20; }
    done
    [ "$(stat -c %s $h)" = "$((HEAD_END+1))" ] || { echo "HEAD SIZE BAD $h"; exit 1; }
    [ -f "$t" ] || nice -n 19 curl -sS -L --fail -D "$path.tailhdr" -r "$((size-TAIL))-$((size-1))" "$url" -o "$t"
    [ "$(stat -c %s $t)" = "$TAIL" ] || { echo "TAIL SIZE BAD"; exit 1; }
    grep -i 'content-range' "$path.tailhdr" | tail -1
    grep -qi "content-range: bytes $((size-TAIL))-$((size-1))/$size" "$path.tailhdr" || { echo "SERVER SIZE != $size"; exit 1; }
    # E: (NTFS via drvfs) does not keep sparse files, so the full-size copy is assembled
    # only for the run (runs/assemble_sparse.sh) and the pieces are what we keep
    echo "pieces head=$(md5sum $h|cut -d' ' -f1) tail=$(md5sum $t|cut -d' ' -f1) server_size=$size server_md5_full=$md5" > "$path.done"
  fi
  echo "$(date -Is) done $path"
done < manifest.tsv
echo ALLDONE
