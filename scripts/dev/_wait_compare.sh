#!/usr/bin/env bash
# Wait for the RAM-staged compare to finish, OR detect a hang (inStrain alive but <2% CPU
# for ~2 min). Emits one terminal line and exits.
stall=0
for i in $(seq 1 40); do   # up to ~20 min
  if grep -q 'compare exit=' /home/allen/compare.log 2>/dev/null; then
    echo "FINISHED: $(grep -hE 'compare exit=' /home/allen/compare.log | tail -1)"
    echo "output: $(ls /mnt/d/bioai/results/compare.IS/output/ 2>/dev/null | tr '\n' ' ')"
    exit 0
  fi
  p=$(ps -eo pcpu,args | grep '[i]nStrain compare' | head -1 | awk '{print $1}')
  if [ -n "$p" ]; then
    if awk -v c="$p" 'BEGIN{exit !(c+0<2.0)}'; then stall=$((stall+1)); else stall=0; fi
    if [ "$stall" -ge 4 ]; then
      echo "HUNG: inStrain compare <2% CPU for ~2min even with profiles in RAM"
      pkill -9 -f 'inStrain compare'
      exit 2
    fi
  fi
  sleep 30
done
echo "TIMEOUT after ~20min without terminal state"
exit 3
