#!/bin/bash

BOT_TOKEN="8509316495:AAEsW2W0vMVbQQ6EvPeti__eD0E0HSUv1SI"
CHAT_ID="-1003871982757"

USER_NAME="$PAM_USER"
HOSTNAME="$(hostname)"
TTY="$PAM_TTY"
RHOST="$PAM_RHOST"
[ -z "$RHOST" ] && RHOST="LOCAL"
TIME="$(date '+%Y-%m-%d %H:%M:%S')"

HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
HIST_FILE="$HOME_DIR/.bash_history"

# Best effort history grab
CMD_HISTORY="(no history)"
if [ -f "$HIST_FILE" ]; then
    CMD_HISTORY="$(tail -n 30 "$HIST_FILE" | sed 's/`/\\`/g')"
fi

MESSAGE="🚪 *Session Closed (PAM)*
👤 User: \`$USER_NAME\`
🖥 Host: \`$HOSTNAME\`
🧵 TTY: \`$TTY\`
🌍 Source: \`$RHOST\`
🕒 Time: \`$TIME\`

📜 *Last Commands*
\`\`\`
$CMD_HISTORY
\`\`\`
"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="$CHAT_ID" \
  -d parse_mode="Markdown" \
  -d text="$MESSAGE" >/dev/null 2>&1

exit 0
