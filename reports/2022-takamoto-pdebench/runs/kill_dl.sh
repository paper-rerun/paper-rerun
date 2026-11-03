pkill -f runs/download_bg.sh; pkill -f runs/download.sh; pkill -f 'curl -sS -L --fail'; sleep 1; pgrep -af curl; echo killed
