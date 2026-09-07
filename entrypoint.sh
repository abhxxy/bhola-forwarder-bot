#!/bin/sh
set -eu

mkdir -p /data
if [ -n "${TELETHON_SESSION_B64:-}" ] && [ ! -s "/data/${SESSION_NAME:-bhola_session}.session" ]; then
  printf '%s' "$TELETHON_SESSION_B64" | base64 -d > "/data/${SESSION_NAME:-bhola_session}.session"
  chmod 600 "/data/${SESSION_NAME:-bhola_session}.session"
fi

cd /data
set +e
python /app/main.py 2>&1 | tee -a /data/runtime.log
status=${PIPESTATUS[0]}
if [ "$status" -ne 0 ]; then
  printf 'Bhola forwarder exited with status %s; keeping container alive for diagnostics.\n' "$status"
  sleep 3600
fi
exit "$status"
