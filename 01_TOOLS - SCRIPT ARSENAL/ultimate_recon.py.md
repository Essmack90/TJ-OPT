
```python
#!/usr/bin/env python3
"""
ultimate_recon.py - Complete reconnaissance automation
Usage: python3 ultimate_recon.py -t 10.10.10.5
"""

import subprocess
import sys
import os
import threading
import time
import socket
import json
from datetime import datetime

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if level == "GOOD":
        print(f"{G}[{timestamp}][+]{X} {msg}")
    elif level == "WARN":
        print(f"{Y}[{timestamp}][!]{X} {msg}")
    elif level == "BAD":
        print(f"{R}[{timestamp}][-]{X} {msg}")
    else:
        print(f"{C}[{timestamp}][*]{X} {msg}")

class UltimateRecon:
    def __init__(self, target, output_dir):
        self.target = target
        self.output_dir = output_dir
        self.findings = {
            "ports": [],
            "web_dirs": [],
            "smb_shares": [],
            "users": [],
            "vulns": []
        }
        os.makedirs(output_dir, exist_ok=True)
    
    def quick_ping_check(self):
        log(f"Checking if {self.target} is alive...")
        response = os.system(f"ping -c 1 -W 1 {self.target} > /dev/null 2>&1")
        if response == 0:
            log(f"Host {self.target} is UP", "GOOD")
            return True
        else:
            log(f"Host {self.target} is DOWN or not responding to ping", "WARN")
            return False
    
    def port_scan_aggressive(self):
        log("Starting aggressive port scan...")
        common_ports = [21,22,23,25,53,80,88,110,111,135,139,143,443,445,
                        993,995,1433,1723,2049,3306,3389,5432,5900,5985,
                        5986,6379,8080,8443,27017]
        
        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    open_ports.append(port)
                    log(f"Port {port} is OPEN", "GOOD")
                sock.close()
            except:
                pass
        
        self.findings["ports"] = open_ports
        return open_ports
    
    def service_enumeration(self):
        log("Enumerating services...")
        services = {}
        
        for port in self.findings["ports"]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target, port))
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                services[port] = banner[:100]
                log(f"Port {port}: {banner[:50]}", "GOOD")
                sock.close()
            except:
                services[port] = "Banner grab failed"
        
        return services
    
    def web_enumeration(self):
        log("Enumerating web directories...")
        web_ports = [80, 443, 8080, 8443, 8000, 8008, 8888]
        web_dirs = ["admin", "login", "wp-admin", "phpmyadmin", "backup", 
                    "uploads", "config", "database", "api", "v1", "v2",
                    "console", "dashboard", "manager", "portal", "cgi-bin",
                    ".git", ".svn", ".env", "robots.txt", "sitemap.xml"]
        
        found_dirs = []
        for port in web_ports:
            if port not in self.findings["ports"]:
                continue
            
            for directory in web_dirs:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    sock.connect((self.target, port))
                    
                    request = f"GET /{directory} HTTP/1.1\r\nHost: {self.target}\r\nConnection: close\r\n\r\n"
                    sock.send(request.encode())
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    
                    if "200 OK" in response or "301" in response or "302" in response:
                        log(f"Found: http://{self.target}:{port}/{directory}", "GOOD")
                        found_dirs.append(f"{port}:{directory}")
                    sock.close()
                except:
                    pass
        
        self.findings["web_dirs"] = found_dirs
        return found_dirs
    
    def smb_enumeration(self):
        if 445 not in self.findings["ports"] and 139 not in self.findings["ports"]:
            log("SMB ports not open, skipping SMB enumeration", "WARN")
            return []
        
        log("Enumerating SMB...")
        shares = []
        
        try:
            result = subprocess.run(
                f"smbclient -N -L //{self.target} 2>/dev/null",
                shell=True, capture_output=True, text=True, timeout=10
            )
            
            for line in result.stdout.splitlines():
                if "Disk" in line:
                    share = line.split()[0].strip()
                    if share not in ["IPC$", "print$"]:
                        log(f"Found SMB share: {share}", "GOOD")
                        shares.append(share)
                        self.findings["smb_shares"].append(share)
        except:
            pass
        
        try:
            result = subprocess.run(
                f"enum4linux -U {self.target} 2>/dev/null | grep 'user:'",
                shell=True, capture_output=True, text=True, timeout=15
            )
            
            users = []
            for line in result.stdout.splitlines():
                if "user:" in line:
                    user = line.split("[")[1].split("]")[0]
                    if user not in ["guest", "nobody"]:
                        users.append(user)
                        log(f"Found user: {user}", "GOOD")
            
            self.findings["users"] = users
        except:
            pass
        
        return shares
    
    def generate_report(self):
        report_file = f"{self.output_dir}/report_{self.target}.html"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>OSCP Recon Report - {self.target}</title>
    <style>
        body {{ font-family: monospace; background: #0a0e27; color: #00ff41; padding: 20px; }}
        h1 {{ color: #ff6b35; border-bottom: 2px solid #ff6b35; }}
        h2 {{ color: #00ff41; margin-top: 30px; }}
        .success {{ color: #00ff41; }}
        .warning {{ color: #ffaa00; }}
        .danger {{ color: #ff3333; }}
        .info {{ color: #00ccff; }}
        pre {{ background: #1a1a2e; padding: 10px; border-left: 3px solid #00ff41; overflow-x: auto; }}
        .box {{ background: #1a1a2e; padding: 15px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>OSCP Recon Report: {self.target}</h1>
    <p class="info">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="box">
        <h2>Open Ports</h2>
        <pre>{', '.join(map(str, self.findings['ports'])) if self.findings['ports'] else 'None found'}</pre>
    </div>
    
    <div class="box">
        <h2>Web Directories</h2>
        <pre>{chr(10).join(self.findings['web_dirs']) if self.findings['web_dirs'] else 'None found'}</pre>
    </div>
    
    <div class="box">
        <h2>SMB Shares</h2>
        <pre>{chr(10).join(self.findings['smb_shares']) if self.findings['smb_shares'] else 'None found'}</pre>
    </div>
    
    <div class="box">
        <h2>Enumerated Users</h2>
        <pre>{chr(10).join(self.findings['users']) if self.findings['users'] else 'None found'}</pre>
    </div>
    
    <div class="box">
        <h2>Next Steps</h2>
        <pre>
1. Run nmap full scan: nmap -p- -sC -sV {self.target}
2. Run web enumeration: python3 web_enum.py -u http://{self.target}
3. Check SMB shares: smbclient -N //{self.target}/share_name
4. Try default credentials on discovered services
5. Check for vulnerabilities: searchsploit [service] [version]
        </pre>
    </div>
</body>
</html>"""
        
        with open(report_file, "w") as f:
            f.write(html)
        
        log(f"Report saved to {report_file}", "GOOD")
        return report_file
    
    def run_all(self):
        log(f"Starting Ultimate Recon on {self.target}", "GOOD")
        start_time = time.time()
        
        if not self.quick_ping_check():
            log("Continuing anyway, host may be firewalled", "WARN")
        
        self.port_scan_aggressive()
        self.service_enumeration()
        self.web_enumeration()
        self.smb_enumeration()
        
        elapsed = time.time() - start_time
        log(f"Recon complete in {elapsed:.1f} seconds", "GOOD")
        log(f"Findings: {len(self.findings['ports'])} ports, {len(self.findings['web_dirs'])} web dirs, {len(self.findings['users'])} users", "GOOD")
        
        self.generate_report()
        return self.findings

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} -t <target_ip> [-o output_dir]")
        sys.exit(1)
    
    target = None
    output_dir = "/tmp/recon"
    
    for i, arg in enumerate(sys.argv):
        if arg == "-t" and i+1 < len(sys.argv):
            target = sys.argv[i+1]
        if arg == "-o" and i+1 < len(sys.argv):
            output_dir = sys.argv[i+1]
    
    if not target:
        print("Error: Target IP required (-t)")
        sys.exit(1)
    
    recon = UltimateRecon(target, output_dir)
    findings = recon.run_all()
    
    print(f"\n{G}[+] Recon complete! Check {output_dir}/report_{target}.html{X}")

if __name__ == "__main__":
    main()