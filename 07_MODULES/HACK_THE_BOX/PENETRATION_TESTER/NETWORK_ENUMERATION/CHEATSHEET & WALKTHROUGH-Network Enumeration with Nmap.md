## Scanning Options

| **Nmap Option** | **Description** |
|---|----|
| `10.10.10.0/24` | Target network range. |
| `-sn` | Disables port scanning. |
| `-Pn` | Disables ICMP Echo Requests |
| `-n` | Disables DNS Resolution. |
| `-PE` | Performs the ping scan by using ICMP Echo Requests against the target. |
| `--packet-trace` | Shows all packets sent and received. |
| `--reason` | Displays the reason for a specific result. |
| `--disable-arp-ping` | Disables ARP Ping Requests. |
| `--top-ports=<num>` | Scans the specified top ports that have been defined as most frequent.  |
| `-p-` | Scan all ports. |
| `-p22-110` | Scan all ports between 22 and 110. |
| `-p22,25` | Scans only the specified ports 22 and 25. |
| `-F` | Scans top 100 ports. |
| `-sS` | Performs an TCP SYN-Scan. |
| `-sA` | Performs an TCP ACK-Scan. |
| `-sU` | Performs an UDP Scan. |
| `-sV` | Scans the discovered services for their versions. |
| `-sC` | Perform a Script Scan with scripts that are categorized as "default". |
| `--script <script>` | Performs a Script Scan by using the specified scripts. |
| `-O` | Performs an OS Detection Scan to determine the OS of the target. |
| `-A` | Performs OS Detection, Service Detection, and traceroute scans. |
| `-D RND:5` | Sets the number of random Decoys that will be used to scan the target. |
| `-e` | Specifies the network interface that is used for the scan. |
| `-S 10.10.10.200` | Specifies the source IP address for the scan. |
| `-g` | Specifies the source port for the scan. |
| `--dns-server <ns>` | DNS resolution is performed by using a specified name server. |




## Output Options


| **Nmap Option** | **Description** |
|---|----|
| `-oA filename` | Stores the results in all available formats starting with the name of "filename". |
| `-oN filename` | Stores the results in normal format with the name "filename". |
| `-oG filename` | Stores the results in "grepable" format with the name of "filename". |
| `-oX filename` | Stores the results in XML format with the name of "filename". |



## Performance Options

| **Nmap Option** | **Description** |
|---|----|
| `--max-retries <num>` | Sets the number of retries for scans of specific ports. |
| `--stats-every=5s` | Displays scan's status every 5 seconds. |
| `-v/-vv` | Displays verbose output during the scan. |
| `--initial-rtt-timeout 50ms` | Sets the specified time value as initial RTT timeout. |
| `--max-rtt-timeout 100ms` | Sets the specified time value as maximum RTT timeout. |
| `--min-rate 300` | Sets the number of packets that will be sent simultaneously. |
| `-T <0-5>` | Specifies the specific timing template. |
# Network Enumeration with Nmap Module

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Host Discovery|Question 1|Windows|
|Host and Port Scanning|Question 1|7|
|Host and Port Scanning|Question 2|NIX-NMAP-DEFAULT|
|Saving the Results|Question 1|31337|
|Service Enumeration|Question 1|HTB{pr0F7pDv3r510nb4nn3r}|
|Nmap Scripting Engine|Question 1|HTB{873nniuc71bu6usbs1i96as6dsv26}|
|Firewall and IDS/IPS Evasion - Easy Lab|Question 1|Ubuntu|
|Firewall and IDS/IPS Evasion - Medium Lab|Question 1|HTB{GoTtgUnyze9Psw4vGjcuMpHRp}|
|Firewall and IDS/IPS Evasion - Hard Lab|Question 1|HTB{kjnsdf2n982n1827eh76238s98di1w6}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Host Discovery

## Question 1

### "Based on the last result, find out which operating system it belongs to. Submit the name of the operating system as result."

When referring to the output of the last `Nmap` scan, students will notice that the `TTL` from the ECHO reply is `128`:

![Network_Enumeration_with_Nmap_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/13/Network_Enumeration_with_Nmap_Walkthrough_Image_1.png)

Performing a quick Google search for `Default TTL values for different OS` will bring up many sites, with the [first](https://subinsb.com/default-device-ttl-values/) showing that `128` belongs to the `Windows` OS:

![Network_Enumeration_with_Nmap_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/13/Network_Enumeration_with_Nmap_Walkthrough_Image_2.png)

Answer: `Windows`

# Host and Port Scanning

## Question 1

### "Find all TCP ports on your target. Submit the total number of found TCP ports as the answer."

Students need to launch an `Nmap` scan against all ports and only show open ports, finding them to be 7:

Code: shell

```shell
sudo nmap --open -p- STMIP -T5
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap --open -p- 10.129.146.165 -T5

Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-28 00:49 BST
Nmap scan report for 10.129.146.165
Host is up (0.27s latency).
Not shown: 65528 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
110/tcp   open  pop3
139/tcp   open  netbios-ssn
143/tcp   open  imap
445/tcp   open  microsoft-ds
31337/tcp open  Elite
```

Instead of counting manually, students can use `grep` and `wc`:

Code: shell

```shell
sudo nmap --open -p- STMIP -T5 | grep "/tcp" | wc -l
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap --open -p- 10.129.146.165 -T5 | grep "/tcp" | wc -l

7
```

Answer: `7`

# Host and Port Scanning

## Question 2

### "Enumerate the hostname of your target and submit it as the answer. (case-sensitive)"

Students need to launch an `Nmap` scan on port 445 and probe it for service/version info, to find that the hostname from the scan's output is `NIX-NMAP-DEFAULT`:

Code: shell

```shell
sudo nmap -p445 STMIP -T5 -sV
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p445 10.129.146.165 -T5 -sV

Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-28 00:59 BST
Nmap scan report for 10.129.146.165
Host is up (0.075s latency).

PORT    STATE SERVICE     VERSION
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
Service Info: Host: NIX-NMAP-DEFAULT

<SNIP>
```

Alternatively, students can also use `grep` and `cut` to only show the hostname alone:

Code: shell

```shell
sudo nmap -p445 STMIP -T5 -sV | grep "Host:" | cut -d "" -f3,4
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p445 10.129.146.165 -T5 -sV | grep "Host:" | cut -d " " -f3,4

Host: NIX-NMAP-DEFAULT
```

Answer: `NIX-NMAP-DEFAULT`

# Saving the Results

## Question 1

### "Perform a full TCP port scan on your target and create an HTML report. Submit the number of the highest port as the answer."

Students need to launch a `Nmap` scan against all ports and only show open ports, saving the output in the XML format:

Code: shell

```shell
sudo nmap --open -p- STMIP -T5 -oX report.xml
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap --open -p- 10.129.146.165 -T5 -oX report.xml

Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-28 01:12 BST
Nmap scan report for 10.129.146.165
Host is up (0.22s latency).
Not shown: 65528 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
110/tcp   open  pop3
139/tcp   open  netbios-ssn
143/tcp   open  imap
445/tcp   open  microsoft-ds
31337/tcp open  Elite
```

Although students have found out that the highest port open is 31337, they are still encouraged to convert `report.xml` to an HTML report using `xsltproc`:

Code: shell

```shell
xsltproc report.xml -o report.html
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xsltproc report.xml -o report.html
```

Then, students can open the report using a browser such as `Firefox`:

Code: shell

```shell
firefox report.html
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ firefox report.html
```

![Network_Enumeration_with_Nmap_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/13/Network_Enumeration_with_Nmap_Walkthrough_Image_3.png)

Answer: `31337`

# Service Enumeration

## Question 1

### "Enumerate all ports and their services. One of the services contains the flag you have to submit as the answer."

Students need to use `nc` on the highest port open, which is 31337 (discovered from the previous question), to attain the flag `HTB{pr0F7pDv3r510nb4nn3r}`:

Code: shell

```shell
nc -nv STMIP 31337
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nv 10.129.2.49 31337

(UNKNOWN) [10.129.2.49] 31337 (?) open
220 HTB{pr0F7pDv3r510nb4nn3r}
```

Answer: `HTB{pr0F7pDv3r510nb4nn3r}`

# Nmap Scripting Engine

## Question 1

### "Use NSE and its scripts to find the flag that one of the services contain and submit it as the answer."

Students first need to launch an `Nmap` scan against port 80 with the `discovery` script or `http-enum`. The former takes quite a while, as it includes many scripts under it, including `http-enum`:

Code: shell

```shell
sudo nmap -p80 STMIP --script discovery
```

```shell-session
┌─[us-academy-1]─[10.10.14.87]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -p80 10.129.146.32 --script discovery

Starting Nmap 7.92 ( https://nmap.org ) at 2022-07-10 07:20 BST
Pre-scan script results:
|_hostmap-robtex: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
| targets-asn: 
|_  targets-asn.asn is a mandatory parameter
|_http-robtex-shared-ns: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
Nmap scan report for 10.129.146.32
Host is up (0.075s latency).

Bug in http-security-headers: no string output.
PORT   STATE SERVICE
80/tcp open  http
|_http-date: Sun, 10 Jul 2022 06:22:33 GMT; +1h01m58s from local time.

<SNIP>

| http-enum: 
|_  /robots.txt: Robots file
| http-vhosts: 
|_128 names had status 200

<SNIP>
```

Once the scan has finished, students will find that there is a "robots.txt" file found by the `http-enum` script, thus, they can use `cURL` to retrieve its contents to attain the flag `HTB{873nniuc71bu6usbs1i96as6dsv26}`:

Code: shell

```shell
curl http://STMIP/robots.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl http://10.129.146.32/robots.txt

User-agent: *

Allow: /

HTB{873nniuc71bu6usbs1i96as6dsv26}
```

Answer: `HTB{873nniuc71bu6usbs1i96as6dsv26}`

# Firewall and IDS/IPS Evasion - Easy Lab

## Question 1

### "Our client wants to know if we can identify which operating system their provided machine is running on. Submit the OS name as the answer."

Students need to launch an `Nmap` scan on the top 20 ports with the `-sV` option, disabling ARP ping, finding the operating system to be `Ubuntu`, as exposed by the version of some of the services:

Code: shell

```shell
sudo nmap -sV --top-ports 10 --disable-arp-ping STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -sV --top-ports 10 --disable-arp-ping 10.129.2.80

Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-28 02:50 BST
Nmap scan report for 10.129.2.80
Host is up (0.077s latency).

PORT     STATE    SERVICE       VERSION
21/tcp   closed   ftp
22/tcp   open     ssh           OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
23/tcp   closed   telnet
25/tcp   filtered smtp
80/tcp   open     http          Apache httpd 2.4.18 ((Ubuntu))
110/tcp  filtered pop3
139/tcp  filtered netbios-ssn
443/tcp  filtered https
445/tcp  filtered microsoft-ds
3389/tcp closed   ms-wbt-server
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

<SNIP>
```

Answer: `Ubuntu`

# Firewall and IDS/IPS Evasion - Medium Lab

## Question 1

### "After the configurations are transferred to the system, our client wants to know if it is possible to find out our target's DNS server version. Submit the DNS server version of the target as the answer."

Students need to launch an `Nmap` scan on port 53, disable ARP ping and (skip) host discovery, use the `-sU` option to make it UDP scan, and `-sC` to use the default scripts, to attain the flag `HTB{GoTtgUnyze9Psw4vGjcuMpHRp}`:

```shell
sudo nmap  -Pn --disable-arp-ping -p53 -sU -sC STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.87]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -Pn --disable-arp-ping -p53 -sU -sC 10.129.2.48

Starting Nmap 7.92 ( https://nmap.org ) at 2022-07-10 08:07 BST
Nmap scan report for 10.129.2.48
Host is up (0.075s latency).

PORT   STATE SERVICE
53/udp open  domain
| dns-nsid: 
|_  bind.version: HTB{GoTtgUnyze9Psw4vGjcuMpHRp}
```

Answer: `HTB{GoTtgUnyze9Psw4vGjcuMpHRp}`

# Firewall and IDS/IPS Evasion - Hard Lab

## Question 1

### "Now our client wants to know if it is possible to find out the version of the running services. Submit the version of the service our client was talking about as the answer."

Students need to launch an `Nmap` scan against all ports, disable ARP ping and (skip) host discovery, and use port 53 as the source port for evasion:

```shell
sudo nmap -g53 --max-retries=1 -Pn -p- --disable-arp-ping STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.87]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -g53 --max-retries=1 -Pn -p- --disable-arp-ping 10.129.142.113

Starting Nmap 7.92 ( https://nmap.org ) at 2022-07-10 10:38 BST
Warning: 10.129.142.113 giving up on port because retransmission cap hit (1).
Nmap scan report for 10.129.142.113
Host is up (0.47s latency).
Not shown: 64562 closed tcp ports (reset), 970 filtered tcp ports (no-response)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
50000/tcp open  ibm-db2
```

Students will find out that port 50000 is open running `IBM Db2`, thus, they need to connect to it using port 53 as the source port to attain the flag `HTB{kjnsdf2n982n1827eh76238s98di1w6}`:

```shell
sudo nc -nv -s PWNIP -p53 STMIP 50000
```

```shell-session
┌─[us-academy-1]─[10.10.14.87]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nc -s 10.10.14.87 -p53 10.129.142.113 50000

220 HTB{kjnsdf2n982n1827eh76238s98di1w6}
```

Answer: `HTB{kjnsdf2n982n1827eh76238s98di1w6}`