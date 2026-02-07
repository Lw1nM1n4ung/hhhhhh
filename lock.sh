# ================================
# 🔐 SHELL KEY PROTECTION
# ================================

# ---- Emergency bypass ----
[[ -f "$HOME/.no_key" ]] && return

# ---- Disable Ctrl+C immediately ----
trap '' SIGINT

# ---- Prevent re-run loop ----
if [[ -z "$SHELL_KEY_OK" ]]; then
    export SHELL_KEY_OK=1

    read -s -p "🔐 Enter production key: " INPUT_KEY
    echo

    # ---- Hash input key ----
    INPUT_HASH="$(printf '%s' "$INPUT_KEY" | sha256sum | awk '{print $1}')"

    # ---- Stored hash ----
    STORED_HASH="bebb73d12f54e5f4323d39c8a1e5c2cb4cc3f19120e6ca5e1185ae7c21dd2f91"

    if [[ "$INPUT_HASH" != "$STORED_HASH" ]]; then
        echo "❌ Access denied"
        exit 1
    fi

    echo "✅ Access granted"
fi
