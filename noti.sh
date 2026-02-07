#!/bin/bash

# === TELEGRAM CONFIG ===
BOT_TOKEN="8509316495:AAEsW2W0vMVbQQ6EvPeti__eD0E0HSUv1SI"
CHAT_ID="-1003871982757"

# Only run for real SSH sessions
[ -z "$SSH_CONNECTION" ] && exit 0

# === SYSTEM INFO ===
USER_NAME="$(whoami)"
HOSTNAME="$(hostname)"
IP_ADDR="$(echo $SSH_CONNECTION | awk '{print $1}')"
PORT="$(echo $SSH_CONNECTION | awk '{print $4}')"
DATE_TIME="$(date '+%Y-%m-%d %H:%M:%S')"

MESSAGE="🚨 *SSH Login Alert*
👤 User: \`$USER_NAME\`
🖥 Host: \`$HOSTNAME\`
🌍 IP: \`$IP_ADDR\`
🔌 Port: \`$PORT\`
🕒 Time: \`$DATE_TIME\`"

# === SEND TELEGRAM MESSAGE ===
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d parse_mode="Markdown" \
  -d text="$MESSAGE" >/dev/null 2>&1
