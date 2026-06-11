```python
#!/usr/bin/env python3
"""
firewall_evasion.py - Bypass firewalls and IDS
Usage: python3 firewall_evasion.py -t 10.10.10.5 --technique all
"""

import argparse
import subprocess
import random
import time

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

class FirewallEvasion:
    def __init__(self, target):
        self.target = target
        
    def fragment_scan(self):
        print(f"{C}[*] Performing fragmented scan...{X}")
        cmd = f"nmap -f -sS -p- {self.target}"
        subprocess.run(cmd, shell=True)
    
    def decoy_scan(self):
        print(f"{C}[*] Performing decoy scan...{X}")
        decoys = f"RND:10,{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        cmd = f"nmap -D {decoys} -sS -p- {self.target}"
        subprocess.run(cmd, shell=True)
    
    def timing_scan(self):
        print(f"{C}[*] Performing slow timing scan...{X}")
        cmd = f"nmap -T1 -sS -p- {self.target}"
        subprocess.run(cmd, shell=True)
    
    def mtu_scan(self):
        print(f"{C}[*] Performing MTU scan...{X}")
        cmd = f"nmap --mtu 8 -sS -p- {self.target}"
        subprocess.run(cmd, shell=True)
    
    def source_port_scan(self):
        print(f"{C}[*] Performing source port scan...{X}")
        cmd = f"nmap --source-port 53 -sS -p- {self.target}"
        subprocess.run(cmd, shell=True)
    
    def idle_scan(self):
        print(f"{C}[*] Finding zombie host for idle scan...{X}")
        cmd = f"nmap -p 80 --open -sL {self.target}/24 | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' | head -1"
        zombie = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
        
        if zombie:
            print(f"{G}[+] Using zombie: {zombie}{X}")
            cmd = f"nmap -sI {zombie} -p- {self.target}"
            subprocess.run(cmd, shell=True)
        else:
            print(f"{R}[-] No suitable zombie found{X}")
    
    def http_tunnel(self):
        print(f"{C}[*] Setting up HTTP tunnel...{X}")
        subprocess.Popen(f"httptunnel -s {self.target} -p 8888", shell=True)
        print(f"{G}[+] HTTP tunnel listening on port 8888{X}")
    
    def dns_tunnel(self):
        print(f"{C}[*] Setting up DNS tunnel...{X}")
        cmd = f"iodine -f -P password {self.target}"
        subprocess.run(cmd, shell=True)
    
    def ssl_tunnel(self):
        print(f"{C}[*] Setting up SSL tunnel...{X}")
        stunnel_conf = f"""
cert = /etc/stunnel/stunnel.pem
client = no
[reverse]
accept = 8888
connect = {self.target}:443
"""
        with open("/tmp/stunnel.conf", "w") as f:
            f.write(stunnel_conf)
        
        subprocess.Popen(f"stunnel /tmp/stunnel.conf", shell=True)
        print(f"{G}[+] SSL tunnel established on port 8888{X}")
    
    def all_techniques(self):
        print(f"{B}{C}=== Running All Evasion Techniques ==={X}\n")
        
        techniques = [
            self.fragment_scan,
            self.decoy_scan,
            self.timing_scan,
            self.mtu_scan,
            self.source_port_scan
        ]
        
        for technique in techniques:
            technique()
            time.sleep(5)
        
        print(f"\n{G}[+] All evasion techniques completed{X}")

def main():
    ap = argparse.ArgumentParser(description="Firewall Evasion Toolkit")
    ap.add_argument("-t", "--target", required=True)
    ap.add_argument("--technique", choices=["fragment", "decoy", "timing", "mtu", "source", "idle", "http", "dns", "ssl", "all"], default="all")
    args = ap.parse_args()
    
    evader = FirewallEvasion(args.target)
    
    print(f"{B}{C}=== Firewall Evasion Toolkit ==={X}\n")
    
    if args.technique == "fragment":
        evader.fragment_scan()
    elif args.technique == "decoy":
        evader.decoy_scan()
    elif args.technique == "timing":
        evader.timing_scan()
    elif args.technique == "mtu":
        evader.mtu_scan()
    elif args.technique == "source":
        evader.source_port_scan()
    elif args.technique == "idle":
        evader.idle_scan()
    elif args.technique == "http":
        evader.http_tunnel()
    elif args.technique == "dns":
        evader.dns_tunnel()
    elif args.technique == "ssl":
        evader.ssl_tunnel()
    elif args.technique == "all":
        evader.all_techniques()

if __name__ == "__main__":
    main()
```