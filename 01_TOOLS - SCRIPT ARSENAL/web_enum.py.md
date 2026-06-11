```python
#!/usr/bin/env python3
"""
web_enum.py - Web directory and file enumeration
Usage: python3 web_enum.py -u http://10.10.10.5 --full
"""

import argparse
import sys
import re
import time
import threading
import queue
from urllib.parse import urljoin

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    print("pip install requests")
    sys.exit(1)

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

def info(s): print(f"{C}[*]{X} {s}")
def good(s): print(f"{G}[+]{X} {s}")
def warn(s): print(f"{Y}[!]{X} {s}")
def bad(s): print(f"{R}[-]{X} {s}")
def head(s): print(f"\n{B}{C}{'-'*60}{X}\n{B}  {s}{X}\n{'-'*60}")

BUILTIN_DIRS = [
    "admin", "administrator", "login", "wp-admin", "phpmyadmin", "dashboard",
    "backup", "backups", "uploads", "images", "img", "static", "assets", "files",
    "includes", "config", "conf", "configuration", "setup", "install", "database",
    "db", "data", "logs", "log", "tmp", "temp", "test", "dev", "development", "old",
    "bak", "src", "source", "api", "v1", "v2", "console", "panel", "manage",
    "management", "portal", "cgi-bin", "scripts", "app", "application", "web",
    ".git", ".svn", ".env", "wp-content", "wp-includes", "vendor", "node_modules",
    "secret", "secrets", "private", "internal", "hidden", "archive",
]

BUILTIN_FILES = [
    "index.php", "index.html", "login.php", "admin.php", "config.php", "db.php",
    "database.php", "wp-config.php", "wp-login.php", "xmlrpc.php",
    ".htaccess", ".htpasswd", ".env", "web.config", "robots.txt", "sitemap.xml",
    "crossdomain.xml", "phpinfo.php", "info.php", "test.php", "shell.php",
    "backup.zip", "backup.tar.gz", "backup.sql", "db.sql", "dump.sql",
    "Dockerfile", "docker-compose.yml", "README.md", "CHANGELOG.md",
    "package.json", "composer.json", "Gemfile", "requirements.txt",
]

DEFAULT_CREDS = [
    ("admin", "admin"), ("admin", "password"), ("admin", "password123"),
    ("admin", "admin123"), ("admin", ""), ("root", "root"), ("root", ""),
    ("administrator", "administrator"), ("test", "test"), ("guest", "guest"),
    ("admin", "1234"), ("admin", "12345"), ("admin", "123456"),
    ("tomcat", "tomcat"), ("manager", "manager"), ("user", "user"),
]

LOGIN_PATHS = [
    "/login", "/login.php", "/admin", "/admin.php", "/admin/login",
    "/wp-login.php", "/administrator", "/user/login", "/auth/login",
    "/account/login", "/signin", "/console", "/panel", "/dashboard",
]

INTERESTING_PATTERNS = [
    (r"sql syntax|mysql_fetch|ORA-\d{5}|sqlite3|pg_query", "Possible SQL error leak"),
    (r"warning.*php.*line", "PHP error disclosure"),
    (r"stack trace|traceback|exception in", "Stack trace disclosure"),
    (r"root:x:0:0", "Possible /etc/passwd leak"),
    (r"password\s*=\s*['\"][^'\"]{3,}", "Possible hardcoded password"),
    (r"aws_access_key_id|aws_secret", "AWS credentials exposed"),
    (r"BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY", "Private key exposed"),
    (r"DB_PASSWORD|DATABASE_URL|REDIS_URL", "Env var credential leak"),
]

class WebClient:
    def __init__(self, base_url, proxy=None, delay=0, timeout=8, threads=10):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64)"
        self.proxies = {"http": proxy, "https": proxy} if proxy else {}
        self.delay = delay
        self.timeout = timeout
        self.threads = threads

    def get(self, path, **kw):
        url = urljoin(self.base + "/", path.lstrip("/"))
        try:
            time.sleep(self.delay)
            r = self.session.get(url, proxies=self.proxies,
                                  timeout=self.timeout, verify=False,
                                  allow_redirects=True, **kw)
            return r
        except Exception:
            return None

    def post(self, path, data):
        url = urljoin(self.base + "/", path.lstrip("/"))
        try:
            time.sleep(self.delay)
            r = self.session.post(url, data=data, proxies=self.proxies,
                                   timeout=self.timeout, verify=False,
                                   allow_redirects=False)
            return r
        except Exception:
            return None

def banner_grab(client):
    head("Banner / Headers")
    r = client.get("/")
    if not r:
        bad("No response from target")
        return {}
    good(f"HTTP {r.status_code} — {len(r.text)} bytes")
    interesting = ["server", "x-powered-by", "x-aspnet-version", "x-generator",
                   "x-drupal-cache", "x-varnish", "via", "set-cookie"]
    headers = {}
    for h in interesting:
        if h in r.headers:
            warn(f"  {h}: {r.headers[h]}")
            headers[h] = r.headers[h]
    sec_headers = ["strict-transport-security", "x-frame-options",
                   "x-content-type-options", "content-security-policy"]
    for h in sec_headers:
        if h not in r.headers:
            info(f"  Missing security header: {h}")
    return headers

def check_robots(client):
    head("robots.txt / sitemap.xml")
    for path in ["/robots.txt", "/sitemap.xml"]:
        r = client.get(path)
        if r and r.status_code == 200:
            good(f"Found: {path}")
            for line in r.text.splitlines()[:30]:
                if line.strip():
                    print(f"  {line}")
        else:
            bad(f"Not found: {path}")

def check_git(client):
    head("Git / SVN / Source Exposure")
    paths = ["/.git/HEAD", "/.git/config", "/.svn/entries",
             "/.env", "/Dockerfile", "/docker-compose.yml"]
    for path in paths:
        r = client.get(path)
        if r and r.status_code == 200 and len(r.text) > 10:
            warn(f"EXPOSED: {path}")
            print(f"  {r.text[:200].strip()}")

def scan_directories(client, wordlist_path=None, extensions=None):
    head("Directory / File Brute Force")
    words = list(BUILTIN_DIRS) + list(BUILTIN_FILES)
    if wordlist_path:
        try:
            with open(wordlist_path) as f:
                words = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            info(f"Loaded {len(words)} words from {wordlist_path}")
        except FileNotFoundError:
            warn(f"Wordlist not found, using built-in list")

    exts = extensions or ["", ".php", ".html", ".txt", ".bak", ".old"]
    paths_to_try = []
    for w in words:
        if "." in w:
            paths_to_try.append(w)
        else:
            for ext in exts:
                paths_to_try.append(w + ext)

    found = []
    q = queue.Queue()
    for p in paths_to_try:
        q.put(p)
    lock = threading.Lock()

    def worker():
        while True:
            try:
                path = q.get_nowait()
            except queue.Empty:
                break
            r = client.get(path)
            if r and r.status_code in [200, 201, 301, 302, 403]:
                with lock:
                    col = G if r.status_code == 200 else Y
                    print(f"  {col}{r.status_code}{X} /{path} ({len(r.text)} bytes)")
                    found.append((r.status_code, path, r.text))
            q.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(client.threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return found

def check_default_creds(client):
    head("Default Credential Check")
    for path in LOGIN_PATHS:
        r = client.get(path)
        if not r or r.status_code not in [200, 401, 403]:
            continue
        good(f"Login page found: {path}")
        if r.status_code == 401:
            warn(f"  HTTP Basic Auth at {path}")
            for user, pw in DEFAULT_CREDS[:5]:
                resp = client.session.get(
                    client.base + path,
                    auth=(user, pw), timeout=5, verify=False
                )
                if resp and resp.status_code == 200:
                    good(f"  VALID BASIC AUTH: {user}:{pw}")
                    break
        if r.status_code == 200 and "password" in r.text.lower():
            warn(f"  Form-based login — try manual default creds")
            print(f"  Common: " + ", ".join(f"{u}:{p}" for u, p in DEFAULT_CREDS[:5]))

def check_interesting_content(found_pages):
    head("Interesting Content in Responses")
    for status, path, body in found_pages:
        if status != 200:
            continue
        for pattern, desc in INTERESTING_PATTERNS:
            if re.search(pattern, body, re.IGNORECASE):
                warn(f"/{path} — {desc}")
                m = re.search(pattern, body, re.IGNORECASE)
                if m:
                    start = max(0, m.start()-30)
                    print(f"  Context: ...{body[start:m.end()+60]}...")
                break

def check_common_vulns(client):
    head("Common Web Vulns (quick check)")
    lfi_paths = [
        "/index.php?page=../../../../etc/passwd",
        "/index.php?file=../../../../etc/passwd",
        "/index.php?include=../../../../etc/passwd",
        "/?page=../../../../etc/passwd",
    ]
    for p in lfi_paths:
        r = client.get(p)
        if r and "root:x:0:0" in r.text:
            warn(f"LFI CONFIRMED: {p}")
            break
    else:
        bad("No obvious LFI on common params")

    r = client.get("/redirect?url=http://example.com")
    if r and r.status_code in [301, 302]:
        loc = r.headers.get("location", "")
        if "example.com" in loc:
            warn("Possible open redirect at /redirect?url=")

    r = client.get("/", headers={"Content-Type": "application/xml"})
    if r and "xml" in r.headers.get("content-type", "").lower():
        warn("Server accepts XML content-type — test for XXE")

def main():
    ap = argparse.ArgumentParser(description="web_enum.py — web surface enumeration")
    ap.add_argument("-u", "--url", required=True, help="Target base URL")
    ap.add_argument("--wordlist", default=None)
    ap.add_argument("--proxy", default=None, help="http://127.0.0.1:8080")
    ap.add_argument("--threads", default=10, type=int)
    ap.add_argument("--delay", default=0.0, type=float)
    ap.add_argument("--extensions", default=None, help="Comma-separated extensions e.g. php,html,txt")
    ap.add_argument("--full", action="store_true", help="Run all checks including default creds")
    args = ap.parse_args()

    exts = None
    if args.extensions:
        exts = [""] + ["." + e.lstrip(".") for e in args.extensions.split(",")]

    client = WebClient(args.url, proxy=args.proxy, delay=args.delay, threads=args.threads)

    print(f"\n{B}{C}web_enum.py — OSCP web enumeration{X}")
    print(f"Target: {args.url}\n")

    banner_grab(client)
    check_robots(client)
    check_git(client)
    found = scan_directories(client, args.wordlist, exts)
    check_interesting_content(found)
    check_common_vulns(client)
    if args.full:
        check_default_creds(client)

if __name__ == "__main__":
    main()
```