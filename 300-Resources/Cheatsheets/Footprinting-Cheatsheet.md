---
tags:
  - cheatsheet
  - footprinting
  - enumeration
  - reference
  - "#footprinting-cheatsheet"
---

# Footprinting Cheatsheet - Complete Command Reference

## Infrastructure-based Enumeration

| Command | Description |
|---------|-------------|
| `curl -s https://crt.sh/?q=<target-domain>\&output=json \| jq .` | Certificate transparency lookup |
| `for i in $(cat ip-addresses.txt); do shodan host $i; done` | Scan each IP in a list using Shodan |
| `whois <domain>` | WHOIS lookup for domain |
| `dig any <domain>` | DNS any query |
| `nslookup <domain>` | DNS lookup |
| `host -t any <domain>` | DNS lookup |

---

## Host-based Enumeration

### #FTP

| Command | Description |
|---------|-------------|
| `ftp <FQDN/IP>` | Interact with FTP service |
| `nc -nv <FQDN/IP> 21` | Connect to FTP using netcat |
| `telnet <FQDN/IP> 21` | Connect to FTP using telnet |
| `openssl s_client -connect <FQDN/IP>:21 -starttls ftp` | Connect to FTPS (encrypted) |
| `wget -m --no-passive ftp://anonymous:anonymous@<target>` | Download all files from anonymous FTP |
| `ftp -a <FQDN/IP>` | Anonymous FTP login |

### #SMB

| Command | Description |
|---------|-------------|
| `smbclient -N -L //<FQDN/IP>` | Null session authentication to list shares |
| `smbclient //<FQDN/IP>/<share>` | Connect to a specific SMB share |
| `rpcclient -U "" <FQDN/IP>` | RPC null session connection |
| `samrdump.py <FQDN/IP>` | Username enumeration using Impacket |
| `smbmap -H <FQDN/IP>` | Enumerate SMB shares |
| `crackmapexec smb <FQDN/IP> --shares -u '' -p ''` | Enumerate shares with null session |
| `enum4linux-ng.py <FQDN/IP> -A` | Comprehensive SMB enumeration |

### #NFS

| Command | Description |
|---------|-------------|
| `showmount -e <FQDN/IP>` | Show available NFS shares |
| `mount -t nfs <FQDN/IP>:/<share> ./target-NFS/ -o nolock` | Mount NFS share |
| `umount ./target-NFS` | Unmount NFS share |
| `rpcinfo -p <FQDN/IP>` | List RPC services |

### #DNS

| Command | Description |
|---------|-------------|
| `dig ns <domain.tld> @<nameserver>` | NS query to specific nameserver |
| `dig any <domain.tld> @<nameserver>` | ANY query to specific nameserver |
| `dig axfr <domain.tld> @<nameserver>` | Zone transfer (AXFR) request |
| `dnsenum --dnsserver <nameserver> --enum -p 0 -s 0 -o found_subdomains.txt -f ~/subdomains.list <domain.tld>` | Subdomain brute forcing |
| `fierce --domain <domain.tld> --dns-server <nameserver>` | Subdomain enumeration |
| `dnsrecon -d <domain.tld> -t axfr` | Zone transfer check |
| `host -l <domain.tld> <nameserver>` | Zone transfer (alternative) |

### #SMTP

| Command | Description |
|---------|-------------|
| `telnet <FQDN/IP> 25` | Connect to SMTP server |
| `nc -nv <FQDN/IP> 25` | Connect using netcat |
| `smtp-user-enum -M VRFY -U users.txt -t <FQDN/IP>` | User enumeration via VRFY |
| `nmap --script smtp-commands -p25 <FQDN/IP>` | List SMTP commands |
| `nmap --script smtp-open-relay -p25 <FQDN/IP>` | Test for open relay |

### #IMAP/POP3

| Command | Description |
|---------|-------------|
| `curl -k 'imaps://<FQDN/IP>' --user <user>:<password>` | Login to IMAPS using cURL |
| `openssl s_client -connect <FQDN/IP>:imaps` | Connect to IMAPS |
| `openssl s_client -connect <FQDN/IP>:pop3s` | Connect to POP3S |
| `telnet <FQDN/IP> 110` | Connect to POP3 (plain) |
| `telnet <FQDN/IP> 143` | Connect to IMAP (plain) |

### #SNMP

| Command | Description |
|---------|-------------|
| `snmpwalk -v2c -c <community string> <FQDN/IP>` | Query OIDs with snmpwalk |
| `onesixtyone -c community-strings.list <FQDN/IP>` | Brute force community strings |
| `braa <community string>@<FQDN/IP>:.1.*` | Brute force OIDs |
| `snmpcheck -t <FQDN/IP> -c <community>` | SNMP enumeration tool |
| `nmap -sU -p161 --script snmp-* <FQDN/IP>` | SNMP enumeration with Nmap |

### #MySQL

| Command | Description |
|---------|-------------|
| `mysql -u <user> -p<password> -h <FQDN/IP>` | Login to MySQL server |
| `nmap -p3306 --script mysql-* <FQDN/IP>` | MySQL enumeration with Nmap |
| `hydra -l root -P passwords.txt mysql://<FQDN/IP>` | MySQL brute force |

### #MSSQL

| Command                                                | Description                       |
| ------------------------------------------------------ | --------------------------------- |
| `mssqlclient.py <user>@<FQDN/IP> -windows-auth`        | Login with Windows authentication |
| `nmap -p1433 --script ms-sql-* <FQDN/IP>`              | MSSQL enumeration with Nmap       |
| `crackmapexec mssql <FQDN/IP> -u <user> -p <password>` | MSSQL login test                  |

### #IPMI

| Command | Description |
|---------|-------------|
| `msf6 auxiliary(scanner/ipmi/ipmi_version)` | IPMI version detection |
| `msf6 auxiliary(scanner/ipmi/ipmi_dumphashes)` | Dump IPMI password hashes |
| `ipmitool -H <FQDN/IP> -U <user> -P <password> user list` | List IPMI users |
| `nmap -sU -p623 --script ipmi-version <FQDN/IP>` | IPMI version scan |

### #Linux #Remote Management

| Command | Description |
|---------|-------------|
| `ssh-audit.py <FQDN/IP>` | SSH security audit |
| `ssh <user>@<FQDN/IP>` | SSH login |
| `ssh -i private.key <user>@<FQDN/IP>` | SSH login with private key |
| `ssh <user>@<FQDN/IP> -o PreferredAuthentications=password` | Force password authentication |
| `rsync -av --list-only rsync://<FQDN/IP>/` | List rsync shares |
| `rsync -av rsync://<FQDN/IP>/<share> ./local-dir/` | Download from rsync share |

### #Windows #Remote Management

| Command | Description |
|---------|-------------|
| `rdp-sec-check.pl <FQDN/IP>` | Check RDP security settings |
| `xfreerdp /u:<user> /p:"<password>" /v:<FQDN/IP>` | RDP login from Linux |
| `evil-winrm -i <FQDN/IP> -u <user> -p <password>` | WinRM login |
| `wmiexec.py <user>:"<password>"@<FQDN/IP> "<system command>"` | Execute command via WMI |
| `crackmapexec winrm <FQDN/IP> -u <user> -p <password>` | Test WinRM credentials |
| `crackmapexec rdp <FQDN/IP> -u <user> -p <password>` | Test RDP credentials |

### #Oracle #TNS

| Command | Description |
|---------|-------------|
| `./odat.py all -s <FQDN/IP>` | Comprehensive Oracle scan |
| `sqlplus <user>/<pass>@<FQDN/IP>/<db>` | Login to Oracle database |
| `nmap -p1521 --script oracle-* <FQDN/IP>` | Oracle enumeration with Nmap |
| `tnscmd10g version -h <FQDN/IP>` | Get TNS version |
| `./odat.py utlfile -s <FQDN/IP> -d <db> -U <user> -P <pass> --sysdba --putFile C:\\insert\\path file.txt ./file.txt` | Upload file with Oracle RDBMS |

---

## Quick Reference by Port

| Port    | Service     | Command Example                                          |
| ------- | ----------- | -------------------------------------------------------- |
| 21      | #FTP        | `ftp <FQDN/IP>`                                          |
| 22      | #SSH        | `ssh <user>@<FQDN/IP>`                                   |
| 23      | #Telnet     | `telnet <FQDN/IP>`                                       |
| 25      | #SMTP       | `nc -nv <FQDN/IP> 25`                                    |
| 53      | #DNS        | `dig any <domain> @<FQDN/IP>`                            |
| 110     | #POP3       | `telnet <FQDN/IP> 110`                                   |
| 111     | #RPC        | `rpcinfo -p <FQDN/IP>`                                   |
| 135     | #WMI        | `wmiexec.py user:pass@<FQDN/IP> cmd.exe`                 |
| 137-139 | #NetBIOS    | `nmblookup -A <FQDN/IP>`                                 |
| 143     | #IMAP       | `telnet <FQDN/IP> 143`                                   |
| 161     | #SNMP       | `snmpwalk -v2c -c public <FQDN/IP>`                      |
| 389     | #LDAP       | `ldapsearch -H ldap://<FQDN/IP> -x -s base`              |
| 445     | #SMB        | `smbclient -N -L //<FQDN/IP>`                            |
| 465     | #SMTPS      | `openssl s_client -connect <FQDN/IP>:465`                |
| 512     | #rexec      | `rexec -l <user> <FQDN/IP> <command>`                    |
| 513     | #rlogin     | `rlogin <FQDN/IP> -l <user>`                             |
| 514     | #rsh        | `rsh <FQDN/IP> -l <user> <command>`                      |
| 587     | #SMTP       | `openssl s_client -connect <FQDN/IP>:587 -starttls smtp` |
| 873     | #rsync      | `rsync rsync://<FQDN/IP>/`                               |
| 993     | #IMAPS      | `openssl s_client -connect <FQDN/IP>:993`                |
| 995     | #POP3S      | `openssl s_client -connect <FQDN/IP>:995`                |
| 1433    | #MSSQL      | `mssqlclient.py user@<FQDN/IP>`                          |
| 1521    | #Oracle     | `./odat.py all -s <FQDN/IP>`                             |
| 2049    | #NFS        | `showmount -e <FQDN/IP>`                                 |
| 3306    | #MySQL      | `mysql -u root -h <FQDN/IP>`                             |
| 3389    | #RDP        | `xfreerdp /v:<FQDN/IP>`                                  |
| 5432    | #PostgreSQL | `psql -h <FQDN/IP> -U postgres`                          |
| 5985    | #WinRM      | `evil-winrm -i <FQDN/IP> -u user -p pass`                |
| 5986    | #WinRM SSL  | `evil-winrm -S -i <FQDN/IP> -u user -p pass`             |

---

## Quick One-Liners

### Check for Anonymous FTP
`nc -nv <IP> 21 | grep "230"`

### Check for Null SMB Session
`smbclient -N -L //<IP>`

### DNS Zone Transfer Attempt
`dig axfr <domain> @<IP>`

### SNMP Public Community Check
`snmpwalk -v2c -c public <IP>`

### NFS Share Enumeration
`showmount -e <IP>`

### SMTP User Enumeration
`smtp-user-enum -M VRFY -U users.txt -t <IP>`

### RDP Info
`nmap -p3389 --script rdp-ntlm-info <IP>`

### WinRM Check
`crackmapexec winrm <IP> -u '' -p ''`

### Oracle SID Brute
`nmap -p1521 --script oracle-sid-brute <IP>`

### IPMI Hash Dump
`msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts <IP>; run; exit"`

---

## Pro Tips

1. Always start with port scanning: `nmap -p- -sV <IP>` to find all services
2. Check for default credentials: Always try admin:admin, root:root, etc.
3. Document everything: Use `-oA` in nmap to save all formats
4. Manual verification: Tools can miss things - always verify manually
5. Check UDP too: Many services run on UDP (SNMP, DNS, TFTP)
6. Version matters: Always note service versions for exploit searching
7. Combine tools: Different tools reveal different information
