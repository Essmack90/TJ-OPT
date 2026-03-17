---
tags: [module/footprinting, smb, samba, windows-sharing, level/beginner]
---

# SMB Enumeration - Beginner's Guide

## What is SMB?

SMB (Server Message Block) is a protocol that allows systems to share files, printers, and other network resources. Think of it as a way to access folders and files on another computer as if they were on your own machine.

### Key Points
- Used primarily by Windows, but also works on Linux/Unix via Samba
- Allows sharing of files, printers, and other resources
- Uses Access Control Lists (ACLs) to manage permissions
- Can be accessed with or without authentication

---

## SMB vs Samba vs CIFS

| Term | What It Is |
|------|------------|
| **SMB** | The original protocol developed by IBM |
| **CIFS** | A dialect of SMB (basically SMB version 1) |
| **Samba** | An open-source implementation of SMB for Linux/Unix |

Samba allows Linux systems to act as SMB servers and communicate with Windows machines.

---

## SMB Versions

| Version | Used In | Key Features |
|---------|---------|--------------|
| CIFS | Windows NT 4.0 | Uses NetBIOS (ports 137-139) |
| SMB 1.0 | Windows 2000 | Direct TCP connection (port 445) |
| SMB 2.0 | Windows Vista | Performance improvements, message signing |
| SMB 2.1 | Windows 7 | Better locking mechanisms |
| SMB 3.0 | Windows 8 | Multichannel, encryption, remote storage |
| SMB 3.1.1 | Windows 10/11 | Integrity checking, AES-128 encryption |

### Important Ports
- **137-139 (UDP/TCP)** - NetBIOS (older systems)
- **445 (TCP)** - Direct SMB (modern systems)

---

## Default Samba Configuration

Samba's configuration file is located at `/etc/samba/smb.conf`

### Basic Structure

[global]
   workgroup = WORKGROUP
   server string = Samba Server
   security = user

[sharename]
   comment = Description
   path = /path/to/share
   browseable = yes
   read only = no
   guest ok = no

### Key Sections

| Section | Purpose |
|---------|---------|
| [global] | Settings that apply to all shares |
| [printers] | Printer sharing configuration |
| [sharename] | Individual file share settings |

---

## Important Samba Settings

| Setting | Description | What It Means |
|---------|-------------|---------------|
| workgroup | Workgroup or domain name | Identifies the network group |
| server string | Description of the server | Shows up when browsing |
| path | Directory being shared | Where the files actually are |
| browseable | Whether share appears in list | If no, you need the exact name |
| read only | Users can only read files | No uploads or changes |
| writable | Users can modify files | Can upload/delete/edit |
| guest ok | Allow access without password | Anonymous access |
| create mask | Permissions for new files | Like 0777 = everyone full access |
| directory mask | Permissions for new folders | Same concept for directories |

---

## Dangerous SMB Settings

These settings are risky but we LOVE finding them:

| Setting | Risk |
|---------|------|
| browseable = yes | Attackers can see all shares |
| read only = no | Attackers can upload files |
| writable = yes | Attackers can modify/delete |
| guest ok = yes | No password needed |
| create mask = 0777 | New files are world-writable |
| directory mask = 0777 | New folders are world-writable |
| enable privileges = yes | May expose privilege assignments |

### Example Dangerous Share

[notes]
   comment = CheckIT
   path = /mnt/notes/
   browseable = yes
   read only = no
   writable = yes
   guest ok = yes
   create mask = 0777
   directory mask = 0777

This share allows ANYONE to read, write, and delete files without a password.

---

## Connecting to SMB Shares

### List Available Shares (Null Session)

smbclient -N -L //10.129.14.128

Output:
Sharename       Type      Comment
---------       ----      -------
print$          Disk      Printer Drivers
home            Disk      INFREIGHT Samba
dev             Disk      DEVenv
notes           Disk      CheckIT
IPC$            IPC       IPC Service (DEVSM)

### Connect to a Specific Share

smbclient //10.129.14.128/notes

Enter password: (just press enter for null session)
Anonymous login successful

smb: \>

---

## Basic SMB Commands

Once connected, you can use these commands:

| Command | Description |
|---------|-------------|
| ls | List files |
| cd directory | Change directory |
| get file | Download a file |
| put file | Upload a file |
| mkdir folder | Create directory |
| rm file | Delete file |
| rmdir folder | Remove directory |
| pwd | Show current directory |
| help | Show all commands |
| !command | Run local system command |
| quit | Exit |

### Example Session

smb: \> ls
  .                                   D        0  Wed Sep 22 18:17:51 2021
  ..                                  D        0  Wed Sep 22 12:03:59 2021
  prep-prod.txt                       N       71  Sun Sep 19 15:45:21 2021

smb: \> get prep-prod.txt
getting file \prep-prod.txt of size 71 as prep-prod.txt

smb: \> !cat prep-prod.txt
[] check your code with the templates
[] run code-assessment.py
[] ...

---

## Checking Samba Status

On the server, administrators can check connections with:

smbstatus

Output shows:
- Who is connected
- Which shares they're using
- What files are locked

---

## Key Takeaways

- SMB is for file/printer sharing across networks
- Ports 139 (NetBIOS) and 445 (direct SMB)
- Samba brings SMB to Linux/Unix
- Anonymous access (null session) may be enabled
- Dangerous settings = guest ok, writable, 0777 masks
- smbclient can list and access shares
- You can download/upload files if permissions allow
- Always check for writeable shares
- Uploading files could lead to RCE if share is web-accessible
- Document all shares and permissions
