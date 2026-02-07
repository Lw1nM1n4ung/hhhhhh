#!/bin/bash

# === TELEGRAM CONFIG ===
BOT_TOKEN="8509316495:AAEsW2W0vMVbQQ6EvPeti__eD0E0HSUv1SI"
CHAT_ID="-1003871982757"

# Only bash sessions
[ -z "$BASH_VERSION" ] && exit 0

USER_NAME="$USER"
HOSTNAME="$(hostname)"
TTY="$(tty)"
IP_ADDR="${SSH_CONNECTION%% *}"
[ -z "$IP_ADDR" ] && IP_ADDR="LOCAL"
LOGOUT_TIME="$(date '+%Y-%m-%d %H:%M:%S')"

# Flush history NOW
history -a

# Last 30 commands
CMD_HISTORY="$(tail -n 30 ~/.bash_history | sed 's/`/\\`/g')"

MESSAGE="🚪 *Session Logout*
👤 User: \`$USER_NAME\`
🖥 Host: \`$HOSTNAME\`
🧵 TTY: \`$TTY\`
🌍 Source: \`$IP_ADDR\`
🕒 Time: \`$LOGOUT_TIME\`

📜 *Last Commands*
\`\`\`
$CMD_HISTORY
\`\`\`
"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="$CHAT_ID" \
  -d parse_mode="Markdown" \
  -d text="$MESSAGE" >/dev/null 2>&1
