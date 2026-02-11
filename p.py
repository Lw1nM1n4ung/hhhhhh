#!/usr/bin/env python3

import smtplib
from email.message import EmailMessage

HOSTS = [
    "10.117.18.111",
    "10.117.18.114",
    "10.117.18.202",
]

MAIL_FROM = "relay-test-sender@outside.invalid"
RCPT_TO = "relay-test-recipient@invalid.invalid"


def test_open_relay(host: str) -> None:
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = RCPT_TO
    msg["Subject"] = "Open relay validation (safe test domains)"
    msg.set_content("Open relay validation using reserved .invalid domains.\n")

    print("=" * 60)
    print(f"Testing {host}:25")

    with smtplib.SMTP(host, 25, timeout=15) as s:
        s.set_debuglevel(1)
        s.ehlo_or_helo_if_needed()
        s.send_message(msg)

    print(f"[OK] Server accepted unauthenticated relay: {host}:25")


def main():
    for host in HOSTS:
        try:
            test_open_relay(host)
        except Exception as e:
            print(f"[FAIL] {host}:25 -> {e}")


if __name__ == "__main__":
    main()
