#!/bin/bash
# Block up to ~9.5 min or until the full run ends/fails, then print status
cd /e/Ciencia/noturno/2024-rasp-weatherbench2/runs/logs
for i in $(seq 57); do
	grep -qE "all done|exit [1-9]|stopping" run_all.log && break
	sleep 10
done
grep -E "start|end|free|stopping|all done" run_all.log | tail -3
current=$(grep start run_all.log | tail -1 | awk '{print $3}')
tail -1 $current.log
