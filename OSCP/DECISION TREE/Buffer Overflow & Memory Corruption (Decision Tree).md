# Buffer Overflow & Memory Corruption, Decision Tree

Part of [[DECISION TREE]]. "I'm mid-exploit against a memory corruption bug, what does this symptom mean." For adapting the surrounding exploit code (cross-compiling, staged/stageless payload choice), see [[Fixing Exploits (Decision Tree)|Fixing Exploits]] instead.

---

### A debugger breakpoint at the expected shellcode address never gets hit, and EIP holds a value that looks like a rotated/shifted version of the expected return address
→ This points at an **offset miscalculation**, not a wrong return address, same bytes shuffled by a small number of positions is the classic signature of a buffer that's landing slightly off-target, not landing on the wrong target entirely
→ Recheck exactly how many padding bytes actually get copied before the return-address bytes, string functions (`strcpy`/`strcat`) that determine length by scanning for a null terminator are a common source of this, a terminator landing one byte early silently shortens what actually gets copied
→ See [[14. Fixing Exploits#14.1.5. Changing the Overflow Buffer|14.1.5]] and mechanics at [[Buffer Overflow & Memory Corruption (Breakdowns)#The Sync Breeze off-by-one: malloc/memset/strcat and a null terminator one byte short|Command Breakdowns]]

### The target's return address lives inside a DLL that isn't actually present on the real target
→ Check the target's loaded modules directly (debugger → attach → Executable Modules) before trusting a hardcoded address from the exploit's own source
→ Options ranked by reliability: (1) recreate the target locally and pull the address from your own debugger, (2) reuse a return address from another **EDB-verified** public exploit against the exact same vulnerability, (3) borrow one from an unrelated exploit targeting the same OS, less reliable, varies with patches/protections, (4) if you only have unprivileged target access, pull the DLL off it yourself and inspect with `objdump`
→ Never trust a return address from a system DLL if ASLR is in play, those addresses randomize every boot, prefer addresses inside the vulnerable app's own non-ASLR modules
→ See [[14. Fixing Exploits#14.1.4. Fixing the Exploit|14.1.4]]

### A target stops responding entirely right after sending a buffer overflow payload
→ Before assuming the exploit is wrong, consider that it may have **crashed the target service**, especially if no listener was even running to catch a shell yet, a crash right where a redirect-to-shellcode should have happened is often a good sign the offset/return-address path is actually correct
→ Reset the target VM via the lab platform, confirm the service is back up (a plain `curl`/connection check) before retrying
→ Always get the listener running **first**, confirmed and left open, before firing the exploit again, never the reverse order
→ Mechanics: [[Buffer Overflow & Memory Corruption (Breakdowns)#A target crash right after an uncaught BOF payload is a good sign, not a failure|Command Breakdowns]]
→ See [[14. Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Module Exercise VM #3]]

### An SEH-based exploit's own header warns the offset depends on the install path
→ This is a genuine "verify, don't trust" situation, same discipline as return-address verification generally. If the target's install path differs from what the exploit author assumed, the SEH offset this exploit hardcodes will be wrong
→ Prefer a different candidate exploit whose assumptions better match your target, or verify the actual install path first if you have any way to check it
→ See [[14. Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Module Exercise VM #3]] (`33326.py`'s own header, a real example of this caveat)

### Need to overwrite a function's return address, or an SEH handler, to actually reach shellcode
→ Classic direct overwrite: point the return address at a `JMP ESP` instruction (ESP is sitting at your own injected data at crash time)
→ SEH-based overflow instead: overwrite the SEH handler with a `pop pop ret` address (redirects back to a short jump in the corrupted `nSEH` field, which hops into a NOP sled), see [[Buffer Overflow & Memory Corruption (Breakdowns)#SEH overwrite: why pop pop ret and a short jump, not a direct return-address overwrite|Command Breakdowns]] for the full mechanics
→ Either way, keep a NOP sled (`\x90` repeated) ahead of the actual shellcode for landing slack, don't trim it
→ See [[14. Fixing Exploits#14.1.1. Buffer Overflow in a Nutshell|14.1.1]]

### CloudMe 1.11.2 restarts after a 1500-byte packet but does not return a shell
→ Verify the loopback mapping reaches 127.0.0.1:8888 and leave the listener running before firing again
→ Keep the EDB-48389 layout: 1052-byte offset, 0x68A842B5 PUSH ESP; RET, 30-byte NOP sled, x86 shellcode, 1500 bytes total
→ If a PowerShell or dropped executable wrapper is blocked, build the same buffer in PHP and send it with fsockopen from the target
→ See [[RUNBOOK V2/Windows - Remote - CloudMe Buffer Overflow]] and [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/06. Information Gathering]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
