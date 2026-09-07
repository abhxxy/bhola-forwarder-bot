#!/bin/sh
set -eu

mkdir -p /data
if [ -n "${TELETHON_SESSION_B64:-}" ] && [ ! -s "/data/${SESSION_NAME:-bhola_session}.session" ]; then
  printf '%s' "$TELETHON_SESSION_B64" | base64 -d > "/data/${SESSION_NAME:-bhola_session}.session"
  chmod 600 "/data/${SESSION_NAME:-bhola_session}.session"
fi

cd /data
exec python /app/main.py
