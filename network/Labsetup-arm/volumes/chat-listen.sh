#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-9000}"
NAME="${2:-$(hostname)}"

echo "[chat-listen] ${NAME} listening on port ${PORT}"
echo "[chat-listen] Ctrl+C to exit"

# Prefix each sent message with timestamp and sender name.
while IFS= read -r line; do
	printf '[%s] %s: %s\n' "$(date +%H:%M:%S)" "$NAME" "$line"
done | nc -lvnp "$PORT"
