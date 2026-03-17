---
tags: [module/footprinting, ftp, tftp, service-enumeration, level/beginner]
---

# FTP Enumeration - Beginner's Guide

## What is FTP?

FTP (File Transfer Protocol) is one of the oldest protocols on the Internet. It runs in the application layer (same as HTTP and POP) and is used for transferring files between clients and servers.

Think of it as a way to upload and download files from a remote system.

---

## How FTP Works

### Two Channels

FTP uses two separate connections:

1. Control Channel (TCP port 21)
   - Sends commands (login, list files, etc.)
   - Receives status codes

2. Data Channel (TCP port 20)
   - Actually transfers file data
   - Opens only when transferring files

### Active vs Passive Mode

| Mode | How It Works | Firewall Issue |
|------|--------------|----------------|
| Active | Server connects BACK to client for data | Client firewall blocks incoming |
| Passive | Client connects to server-specified port | Works through client firewalls |

Important: Passive mode was developed because client firewalls block incoming connections.

---

## FTP Security

### What You NEED to Know

1. FTP is CLEAR-TEXT - credentials and data are sent UNENCRYPTED
2. Anyone on the network can sniff FTP traffic
3. Credentials can be captured with tools like Wireshark

### Anonymous FTP

Some servers allow anonymous login:
- Username: anonymous
- Password: anonymous or any email

This is often used for public file sharing, but can be a security risk.

---

## TFTP - The Simpler Cousin

### Trivial File Transfer Protocol

| Feature | FTP | TFTP |
|---------|-----|------|
| Port | TCP 21/20 | UDP 69 |
| Authentication | Username/password | NONE |
| Reliability | TCP guarantees delivery | UDP (unreliable) |
| Directory listing | YES | NO |
| Security | Clear-text but has auth | NO AUTH AT ALL |
| Use case | General file transfer | Local networks, firmware updates |

### TFTP Commands

| Command | Description |
|---------|-------------|
| connect | Set remote host |
| get | Download file |
| put | Upload file |
| quit | Exit |
| status | Show current settings |
| verbose | Toggle detailed output |

Limitation: TFTP cannot list directories - you need to KNOW the filename.

---

## Common FTP Server: vsFTPd

vsFTPd is one of the most popular FTP servers on Linux.

### Installation

sudo apt install vsftpd

### Default Configuration File

/etc/vsftpd.conf

### Important Default Settings

| Setting | Default | Meaning |
|---------|---------|---------|
| anonymous_enable=NO | Disabled | Anonymous login off by default |
| local_enable=YES | Enabled | Local users can login |
| write_enable=YES | Enabled | Users can upload/modify files |
| chroot_local_user=YES | Often set | Users confined to home dir |

### The ftpusers File

/etc/ftpusers contains users DENIED access to FTP

Example:
guest
john
kevin

---

## Dangerous FTP Settings

These settings make FTP less secure (but we love finding them):

| Setting | Description | What It Means For Us |
|---------|-------------|----------------------|
| anonymous_enable=YES | Allow anonymous login | We can log in without credentials |
| anon_upload_enable=YES | Anonymous can upload | We can drop files |
| anon_mkdir_write_enable=YES | Anonymous can create dirs | More upload options |
| no_anon_password=YES | No password for anonymous | Even easier access |
| write_enable=YES | Allow write commands | Can upload/delete/rename |
| chown_uploads=YES | Change ownership of uploads | May hide our tracks |

---

## Connecting to FTP

### Basic FTP Client

ftp 10.129.14.136

### Anonymous Login

Name: anonymous
Password: anonymous

### What You See

Connected to 10.129.14.136.
220 Welcome to the HTB Academy vsFTP service.
Name: anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.

ftp> ls

200 PORT command successful.
150 Here comes the directory listing.
-rw-rw-r--    1 1002     1002      8138592 Sep 14 16:54 Calender.pptx
drwxrwxr-x    2 1002     1002         4096 Sep 14 16:50 Clients
drwxrwxr-x    2 1002     1002         4096 Sep 14 16:50 Documents
drwxrwxr-x    2 1002     1002         4096 Sep 14 16:50 Employees
-rw-rw-r--    1 1002     1002           41 Sep 14 16:45 Important Notes.txt
226 Directory send OK.

---

## Useful FTP Commands Inside the Client

| Command | Description |
|---------|-------------|
| ls | List files |
| cd directory | Change directory |
| get filename | Download a file |
| put filename | Upload a file |
| delete filename | Remove a file |
| mkdir directory | Create directory |
| pwd | Show current directory |
| status | Show connection status |
| debug | Turn on debugging |
| trace | Show packet trace |
| quit | Exit |

---

## Enabling Debug and Trace

ftp> debug
Debugging on (debug=1).

ftp> trace
Packet tracing on.

ftp> ls
---> PORT 10,10,14,4,188,195
200 PORT command successful. Consider using PASV.
---> LIST
150 Here comes the directory listing.
-rw-rw-r--    1 1002     1002      8138592 Sep 14 16:54 Calender.pptx
226 Directory send OK.

This shows the actual commands being sent to the server.

---

## Downloading Files

### Single File

ftp> get Important\ Notes.txt
local: Important Notes.txt remote: Important Notes.txt
200 PORT command successful.
150 Opening BINARY mode data connection for Important Notes.txt (41 bytes).
226 Transfer complete.
41 bytes received in 0.00 secs

ftp> quit
221 Goodbye.

### Download ALL Files

wget -m --no-passive ftp://anonymous:anonymous@10.129.14.136

This creates a directory named after the IP with all files.

---

## Uploading Files

### Create a Local File

touch testupload.txt

### Upload It

ftp> put testupload.txt
local: testupload.txt remote: testupload.txt
200 PORT command successful.
150 Ok to send data.
226 Transfer complete.

ftp> ls
-rw-------    1 1002     133             0 Sep 15 14:57 testupload.txt

---

## Key Takeaways

- FTP uses two channels: control (21) and data (20)
- Passive mode works through firewalls, active mode often blocked
- FTP is clear-text - credentials can be sniffed
- Anonymous login may be enabled
- TFTP has NO authentication and NO directory listing
- vsFTPd config is at /etc/vsftpd.conf
- /etc/ftpusers lists denied users
- Dangerous settings = anonymous upload, write enable
- Use debug and trace to see what's happening
- wget -m downloads everything recursively
- Upload capabilities can lead to RCE if FTP root is web-accessible
