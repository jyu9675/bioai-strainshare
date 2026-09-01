#!/usr/bin/env bash
# Test whether profile HDF5/data files on /mnt/d are readable (detect USB/DrvFs I/O errors).
P=/mnt/d/bioai/results/profiles
ok=0; bad=0
for d in "$P"/*.IS; do
  f="$d/raw_data/covT.hd5"
  [[ -f "$f" ]] || continue
  if dd if="$f" of=/dev/null bs=1M >/dev/null 2>&1; then
    ok=$((ok+1))
  else
    echo "IO ERROR: $(basename "$d")/raw_data/covT.hd5"
    bad=$((bad+1))
  fi
done
echo "readable covT files: $ok   I/O errors: $bad"
