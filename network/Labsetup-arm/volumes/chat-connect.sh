#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: chat-connect.sh <peer-ip> [port] [name]"
  exit 1
fi

PEER_IP="$1"
PORT="${2:-9000}"
NAME="${3:-$(hostname)}"

echo "[chat-connect] ${NAME} connecting to ${PEER_IP}:${PORT}"
echo "[chat-connect] Ctrl+C to exit"

# Prefix each sent message with timestamp and sender name.
while IFS= read -r line; do
  printf '[%s] %s: %s\n' "$(date +%H:%M:%S)" "$NAME" "$line"
done | nc -nv "$PEER_IP" "$PORT"
