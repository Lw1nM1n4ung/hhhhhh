#!/bin/bash

# === TELEGRAM CONFIG ===
BOT_TOKEN="8509316495:AAEsW2W0vMVbQQ6EvPeti__eD0E0HSUv1SI"
CHAT_ID="-1003871982757"

# Only SSH sessions
[ -z "$SSH_CONNECTION" ] && exit 0

USER_NAME="$(whoami)"
HOSTNAME="$(hostname)"
IP_ADDR="$(echo $SSH_CONNECTION | awk '{print $1}')"
LOGOUT_TIME="$(date '+%Y-%m-%d %H:%M:%S')"

# Save history immediately
history -a

# Get last 30 commands
CMD_HISTORY="$(tail -n 30 ~/.bash_history | sed 's/`/\\`/g')"

MESSAGE="🚪 *SSH Logout Alert*
👤 User: \`$USER_NAME\`
🖥 Host: \`$HOSTNAME\`
🌍 IP: \`$IP_ADDR\`
🕒 Logout: \`$LOGOUT_TIME\`

📜 *Last Commands*
\`\`\`
$CMD_HISTORY
\`\`\`
"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d parse_mode="Markdown" \
  -d text="$MESSAGE" >/dev/null 2>&1
