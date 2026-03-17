---
tags: [module/footprinting, nfs, network-file-system, linux-sharing, level/beginner]
---

# NFS Enumeration - Beginner's Guide

## What is NFS?

NFS (Network File System) is a protocol developed by Sun Microsystems that allows a system to share files and directories with others over a network. It serves the same purpose as SMB, but is designed for Linux/Unix systems.

Think of it as a way to mount a remote folder so it appears as if it's part of your local file system.

---

## Key Differences: NFS vs SMB

| Feature | NFS | SMB |
|---------|-----|-----|
| Platform | Linux/Unix | Primarily Windows |
| Authentication | UID/GID based | User/password |
| Encryption | Limited (NFSv4 adds Kerberos) | Supported |
| Default port | 2049 (plus RPC on 111) | 445 |

Important: NFS clients cannot talk directly to SMB servers. They are different protocols.

---

## NFS Versions

| Version | Key Features |
|---------|--------------|
| NFSv2 | Old, uses UDP, limited file sizes |
| NFSv3 | More features, variable file sizes, better error reporting |
| NFSv4 | Kerberos support, works through firewalls, no portmapper needed, ACLs, stateful |
| NFSv4.1 | Parallel NFS (pNFS), multipathing |
| NFSv4.2 | Server-side copy, space reservation |

Important: NFSv4 uses only port 2049 (TCP/UDP), making it firewall-friendly.

---

## How NFS Works

NFS relies on RPC (Remote Procedure Call) which runs on port 111.

1. Client requests access via RPC
2. Server authenticates based on client's UID/GID
3. Client mounts the remote folder
4. Files appear and behave as if they're local

### Authentication Problem

NFS itself has NO authentication mechanism. Instead:

- It relies on RPC for authentication
- Authentication is based on UID/GID numbers
- Client and server may have different user mappings
- The server doesn't check if UIDs match actual users

This means: If your local UID is 1000, and a file on the server belongs to UID 1000, you can access it - even if you're a different user!

---

## Default Configuration

The main configuration file is `/etc/exports`

### Basic Syntax

/shared/folder client(options)

Examples from default config:
/srv/homes hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
/srv/nfs4 gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)

### Creating a Share

echo '/mnt/nfs 10.129.14.0/24(sync,no_subtree_check)' >> /etc/exports
systemctl restart nfs-kernel-server
exportfs

This shares `/mnt/nfs` to all hosts in the 10.129.14.0/24 network.

---

## NFS Export Options

| Option | Description |
|--------|-------------|
| rw | Read and write permissions |
| ro | Read only permissions |
| sync | Synchronous data transfer (slower but safer) |
| async | Asynchronous data transfer (faster but risky) |
| secure | Require ports below 1024 (root only) |
| insecure | Allow ports above 1024 |
| no_subtree_check | Disable subdirectory checking (performance) |
| root_squash | Map root user to anonymous (prevents root access) |
| no_root_squash | Root keeps root permissions (DANGEROUS) |
| all_squash | Map ALL users to anonymous |
| anonuid | Specify UID for anonymous user |
| anongid | Specify GID for anonymous group |

---

## Dangerous NFS Settings

| Setting | Risk |
|---------|------|
| insecure | Users can connect from high ports (avoiding root restrictions) |
| no_root_squash | Root on client = root on server (CRITICAL) |
| rw | Write access to shares |
| all_squash | All users map to anonymous - but if anonuid=0, that's root! |

### The no_root_squash Danger

If a share has `no_root_squash`, any root user on a client machine can access files as root on the server. This can lead to complete system compromise.

---

## Footprinting NFS

### Key Ports

| Port | Service |
|------|---------|
| 111 | rpcbind (RPC service mapper) |
| 2049 | NFS itself |
| Various | mountd, nlockmgr (dynamically assigned) |

### Basic Nmap Scan

nmap -p111,2049 -sV -sC 10.129.14.128

### NFS-Specific Nmap Scripts

nmap --script nfs* -p111,2049 10.129.14.128 -sV

---

## Enumerating NFS Shares

### Show Available Shares

showmount -e 10.129.14.128

Output:
Export list for 10.129.14.128:
/mnt/nfs 10.129.14.0/24

### List Mounted Shares (if you gain access)

showmount -a 10.129.14.128

---

## Mounting an NFS Share

### Step 1: Create a Mount Point

mkdir target-NFS

### Step 2: Mount the Share

sudo mount -t nfs 10.129.14.128:/mnt/nfs target-NFS/ -o nolock

Note: The `-o nolock` disables file locking, often needed for older NFS versions.

### Step 3: Browse the Contents

cd target-NFS
ls -la

You should see the remote files as if they were local.

---

## Understanding File Permissions on Mounted Shares

### View with Usernames

ls -l

Output:
-rw-r--r-- 1 cry0l1t3 cry0l1t3 1872 Sep 25 00:55 cry0l1t3.priv
-rw-r--r-- 1 root     root     1872 Sep 19 17:27 id_rsa

### View with UIDs (more accurate)

ls -n

Output:
-rw-r--r-- 1 1000 1000 1872 Sep 25 00:55 cry0l1t3.priv
-rw-r--r-- 1    0    0 1872 Sep 19 17:27 id_rsa

This shows the actual UID/GID numbers, which is critical because your local system may map them differently.

---

## The UID Mapping Problem

If a file belongs to UID 1000 on the server, and your local user has UID 1000, you can access it - even if you're a different user!

### Creating a Local User with Matching UID

If you find files owned by UID 1000, create a matching user:

sudo useradd -u 1000 tempuser
sudo -u tempuser bash

Now you can access those files.

---

## Downloading Files from NFS

Once mounted, you can copy files normally:

cp id_rsa ~/
chmod 600 id_rsa
ssh -i id_rsa user@target

---

## Uploading Files to NFS

If the share is writable (rw option):

cp shell.php target-NFS/

If the share is web-accessible, this could lead to RCE.

---

## Unmounting NFS Shares

When done:

cd ..
sudo umount target-NFS

---

## Key Takeaways

- NFS is Linux/Unix file sharing, SMB is Windows
- Uses RPC on port 111, NFS on port 2049
- Authentication is based on UID/GID, not usernames
- The same UID on client = same access as that user on server
- showmount -e lists available shares
- mount -t nfs mounts remote shares locally
- Check for no_root_squash - allows root access
- Dangerous settings = no_root_squash, insecure, rw
- Always check file ownership with ls -n to see actual UIDs
- Create local users with matching UIDs to access files
- Mount and unmount carefully
