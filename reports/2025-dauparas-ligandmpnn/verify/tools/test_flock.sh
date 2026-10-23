#!/bin/bash
# Does the GPU lock actually serialise?
#
# Four run.py processes were on the card at once, all of them launched under
# "flock /mnt/e/Ciencia/.gpu.lock". That lock file sits on a DrvFs mount (the
# Windows E: drive), where advisory locks are not necessarily honoured between
# processes. Test it: hold the lock, then try to take it non-blocking.
LOCK=/mnt/e/Ciencia/.gpu.lock

flock "$LOCK" sleep 8 &
holder=$!
sleep 2

if flock -n "$LOCK" true; then
	echo "BROKEN: acquired $LOCK while another process held it"
else
	echo "OK: $LOCK is honoured, second taker had to wait"
fi

# and the same test on a lock file inside the Linux filesystem, for contrast
LOCAL=$(mktemp)
flock "$LOCAL" sleep 8 &
holder2=$!
sleep 2
if flock -n "$LOCAL" true; then
	echo "BROKEN: acquired the ext4 lock $LOCAL while held"
else
	echo "OK: an ext4 lock file is honoured"
fi

wait $holder $holder2 2>/dev/null
rm -f "$LOCAL"
