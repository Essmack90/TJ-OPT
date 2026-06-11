```python
#!/usr/bin/env python3
"""
privesc_checklist.py - Linux/Windows privilege escalation enumeration
Usage: python3 privesc_checklist.py --all --output privesc.txt
"""

import argparse
import subprocess
import os
import sys
import re
import platform
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

OUTPUT_LINES = []

def out(s):
    OUTPUT_LINES.append(re.sub(r'\033\[\d+m', '', s))
    print(s)

def run(cmd, shell=True, timeout=10):
    try:
        r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception:
        return ""

def linux_system_info():
    head("System Info")
    checks = [
        ("Hostname", "hostname"),
        ("Kernel", "uname -a"),
        ("OS", "cat /etc/os-release 2>/dev/null || cat /etc/issue"),
        ("Arch", "uname -m"),
        ("Current user", "id"),
        ("Uptime", "uptime"),
    ]
    for label, cmd in checks:
        result = run(cmd)
        if result:
            out(f"  {label:15}: {result.splitlines()[0]}")

def linux_users():
    head("Users & Groups")
    out(f"  {run('id')}")
    out(f"  Groups: {run('groups')}")

    passwd = run("cat /etc/passwd")
    shell_users = [l for l in passwd.splitlines() if l.endswith(("sh", "bash", "zsh", "fish")) and not l.startswith("#")]
    if shell_users:
        warn(f"Users with shells:")
        for u in shell_users:
            out(f"    {u.split(':')[0]}")

    sudo_out = run("sudo -l 2>/dev/null")
    if sudo_out and "not allowed" not in sudo_out.lower():
        warn(f"sudo -l output:")
        for line in sudo_out.splitlines():
            out(f"  {line}")
        if "NOPASSWD" in sudo_out:
            good("  NOPASSWD sudo found — check GTFOBins for this binary!")

    if os.access("/etc/passwd", os.W_OK):
        warn("/etc/passwd is WRITABLE — can add root user")

    shadow = run("cat /etc/shadow 2>/dev/null | head -5")
    if shadow and "Permission denied" not in shadow:
        warn("/etc/shadow READABLE:")
        out(shadow[:200])

def linux_suid_sgid():
    head("SUID / SGID Binaries")
    suid = run("find / -perm -4000 -type f 2>/dev/null")
    sgid = run("find / -perm -2000 -type f 2>/dev/null")

    known_suid = {
        "nmap", "vim", "vi", "nano", "find", "bash", "sh", "python", "python3",
        "perl", "ruby", "php", "awk", "gawk", "nawk", "more", "less", "man",
        "cp", "mv", "env", "tee", "wget", "curl", "tar", "zip", "unzip",
        "docker", "pkexec", "doas", "sudo", "su", "newgrp", "passwd",
        "chsh", "chfn", "mount", "umount", "fusermount", "crontab",
        "at", "taskset", "ionice", "watch", "strace", "ltrace",
        "gdb", "node", "npm", "pip", "pip3", "ansible", "puppet",
        "git", "svn", "ed", "emacs", "screen", "tmux", "ftp", "sftp",
    }

    warn("SUID binaries (check GTFOBins for each):")
    for path in suid.splitlines():
        binary = os.path.basename(path)
        marker = f" {G}< GTFOBins{X}" if binary.lower() in known_suid else ""
        out(f"  {path}{marker}")

    if sgid.strip():
        info("SGID binaries:")
        for path in sgid.splitlines()[:10]:
            out(f"  {path}")

def linux_capabilities():
    head("Linux Capabilities")
    caps = run("getcap -r / 2>/dev/null")
    if caps:
        warn("Capabilities set:")
        for line in caps.splitlines():
            out(f"  {line}")
            if any(c in line for c in ["cap_setuid", "cap_net_raw", "cap_dac_override", "ep"]):
                good(f"    Potentially exploitable — check GTFOBins")
    else:
        bad("No capabilities found or getcap not available")

def linux_writable_paths():
    head("Writable Files & Directories")
    path_dirs = os.environ.get("PATH", "").split(":")
    for d in path_dirs:
        if os.path.isdir(d) and os.access(d, os.W_OK):
            warn(f"Writable PATH directory: {d} — PATH hijack possible")

    ww = run("find /etc /usr /opt /var /tmp /dev -maxdepth 3 -writable -type d 2>/dev/null | grep -v proc")
    if ww:
        info("World-writable directories (sample):")
        for d in ww.splitlines()[:15]:
            out(f"  {d}")

def linux_cron():
    head("Cron Jobs")
    cron_locations = [
        "/etc/crontab", "/etc/cron.d/", "/etc/cron.daily/",
        "/etc/cron.hourly/", "/etc/cron.weekly/", "/var/spool/cron/crontabs/"
    ]
    for loc in cron_locations:
        if os.path.isfile(loc):
            content = run(f"cat {loc}")
            if content:
                warn(f"Contents of {loc}:")
                out(content[:500])
        elif os.path.isdir(loc):
            files = run(f"ls -la {loc} 2>/dev/null")
            if files:
                out(f"  {loc}: {files[:200]}")

    user_cron = run("crontab -l 2>/dev/null")
    if user_cron and "no crontab" not in user_cron.lower():
        warn(f"Current user crontab:\n{user_cron}")

    info("Running 5s process snapshot...")
    ps1 = set(run("ps aux --no-headers 2>/dev/null").splitlines())
    import time
    time.sleep(5)
    ps2 = set(run("ps aux --no-headers 2>/dev/null").splitlines())
    new_procs = ps2 - ps1
    if new_procs:
        warn("New processes appeared in 5s window:")
        for p in new_procs:
            out(f"  {p[:120]}")

def linux_services_ports():
    head("Internal Services / Open Ports")
    netstat = run("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
    out(netstat[:1000] if netstat else "  Could not get socket info")

def linux_sensitive_files():
    head("Sensitive Files")
    targets = [
        "/root/.ssh/id_rsa", "/root/.ssh/authorized_keys",
        "~/.ssh/id_rsa", "~/.bash_history", "~/.bashrc",
        "/etc/ssh/sshd_config", "/etc/mysql/my.cnf",
        "/var/www/html/config.php", "/var/www/html/wp-config.php",
        "/home/*/.ssh/id_rsa", "/home/*/.bash_history",
    ]
    for t in targets:
        result = run(f"cat {t} 2>/dev/null | head -20")
        if result and "No such file" not in result and "Permission denied" not in result:
            warn(f"Readable: {t}")
            out(result[:300])

    grep_out = run("grep -rn 'password\\s*=' /var/www /opt /etc/nginx /etc/apache2 2>/dev/null | grep -v '.pyc' | head -20")
    if grep_out:
        warn("Password strings in config files:")
        out(grep_out[:500])

def linux_kernel_exploits():
    head("Kernel Version / Known Local Exploits")
    kernel = run("uname -r")
    out(f"  Kernel: {kernel}")
    kernel_cves = [
        (r"[23]\.\d", "CVE-2016-5195", "DirtyCow — reliable on 2.x/3.x kernels"),
        (r"[34]\.\d\.\d", "CVE-2017-16995", "eBPF verifier bug"),
        (r"5\.[0-7]\.", "CVE-2021-3493", "Ubuntu OverlayFS privesc"),
        (r"5\.[0-9]\.", "CVE-2021-4034", "PwnKit pkexec privesc"),
        (r"[345]\.\d", "CVE-2022-0847", "DirtyPipe — kernel 5.8–5.16"),
    ]
    for pattern, cve, desc in kernel_cves:
        if re.search(pattern, kernel):
            warn(f"  Possible: {cve} — {desc}")

def run_linux_checks(checks):
    fn_map = {
        "system": linux_system_info,
        "users": linux_users,
        "suid": linux_suid_sgid,
        "capabilities": linux_capabilities,
        "writable": linux_writable_paths,
        "cron": linux_cron,
        "ports": linux_services_ports,
        "files": linux_sensitive_files,
        "kernel": linux_kernel_exploits,
    }
    for name, fn in fn_map.items():
        if name in checks:
            fn()

def win_system_info():
    head("System Info")
    for label, cmd in [
        ("Hostname", "hostname"),
        ("OS", "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\""),
        ("User", "whoami /all"),
        ("Hotfixes", "wmic qfe get Caption,Description,HotFixID,InstalledOn 2>nul | head -10"),
    ]:
        out(f"  {label}:\n{run(cmd)[:300]}\n")

def win_unquoted_services():
    head("Unquoted Service Paths")
    result = run('wmic service get name,displayname,pathname,startmode 2>nul | findstr /i "auto" | findstr /i /v "c:\\windows\\\\" | findstr /i /v \'"\'')
    if result:
        warn("Unquoted service paths found:")
        out(result[:500])
    else:
        bad("None found (or wmic unavailable)")

def win_weak_service_perms():
    head("Weak Service Permissions")
    result = run("accesschk.exe -uwcqv * 2>nul | head -30")
    if not result:
        info("accesschk not available — try: sc qc <service> manually")
    else:
        out(result[:500])

def win_autorun():
    head("Autoruns / Registry Persistence")
    reg_paths = [
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
    ]
    for path in reg_paths:
        out(f"\n  {path}:")
        out(run(f'reg query "{path}" 2>nul')[:300])

def win_creds():
    head("Credential Hunting")
    for f in [r"C:\Windows\Repair\SAM", r"C:\Windows\System32\config\SAM"]:
        if os.path.exists(f):
            warn(f"SAM file accessible: {f}")

    unattended = [
        r"C:\Windows\sysprep\sysprep.xml",
        r"C:\Windows\sysprep\sysprep.inf",
        r"C:\Windows\system32\sysprep\sysprep.xml",
        r"C:\unattend.xml",
        r"C:\autounattend.xml",
    ]
    for f in unattended:
        if os.path.exists(f):
            warn(f"Unattended file: {f}")
            out(run(f"type {f}")[:300])

    out(run(r'findstr /si password *.txt *.ini *.config 2>nul | head -10')[:300])
    out(run("cmdkey /list 2>nul")[:200])

def win_always_install_elevated():
    head("AlwaysInstallElevated Check")
    hklm = run(r"reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>nul")
    hkcu = run(r"reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>nul")
    if "0x1" in hklm and "0x1" in hkcu:
        warn("AlwaysInstallElevated is ENABLED — generate MSI payload with msfvenom!")
    else:
        bad("AlwaysInstallElevated not enabled")

def win_writable_paths():
    head("Writable Service Executables")
    services = run('wmic service get pathname 2>nul')
    for line in services.splitlines():
        line = line.strip().strip('"')
        if line and os.path.isfile(line):
            if os.access(line, os.W_OK):
                warn(f"Writable service binary: {line}")

def run_windows_checks():
    win_system_info()
    win_unquoted_services()
    win_weak_service_perms()
    win_autorun()
    win_creds()
    win_always_install_elevated()
    win_writable_paths()

LINUX_CHECKS_ALL = ["system", "users", "suid", "capabilities", "writable", "cron", "ports", "files", "kernel"]

def main():
    ap = argparse.ArgumentParser(description="privesc_checklist.py — post-shell privesc enum")
    ap.add_argument("--linux", action="store_true")
    ap.add_argument("--windows", action="store_true")
    ap.add_argument("--all", action="store_true", help="Run all checks")
    ap.add_argument("--checks", default=None, help="Comma-separated: system,users,suid,cron,...")
    ap.add_argument("--output", default=None, help="Save output to file")
    args = ap.parse_args()

    is_windows = platform.system().lower() == "windows"
    print(f"\n{B}{C}privesc_checklist.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}{X}\n")

    if args.windows or is_windows:
        run_windows_checks()
    else:
        checks = LINUX_CHECKS_ALL
        if args.checks:
            checks = [c.strip() for c in args.checks.split(",")]
        run_linux_checks(checks)

    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(OUTPUT_LINES))
        good(f"Output saved to {args.output}")

if __name__ == "__main__":
    main()
```