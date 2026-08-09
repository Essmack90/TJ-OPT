# Buffer Overflow & Memory Corruption, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Stack overflow mechanics from [[Fixing Exploits]]. See that page for the entry format.

---

## The Sync Breeze off-by-one: `malloc`/`memset`/`strcat` and a null terminator one byte short

**Full mechanism:**
```c
int initial_buffer_size = 780;
char *padding = malloc(initial_buffer_size);
memset(padding, 0x41, initial_buffer_size);
memset(padding + initial_buffer_size - 1, 0x00, 1);
// ... later ...
strcat(buffer, padding);
```

**Piece by piece:**
- `malloc(780)` allocates exactly 780 raw bytes, no more, no less.
- `memset(padding, 0x41, 780)` fills **all 780** of those bytes with `A` (`0x41`).
- The second `memset` immediately overwrites the **very last** of those 780 bytes with `0x00`, so the buffer is actually 779 real `A`s followed by one null byte, not 780 clean `A`s.
- `strcat()` (and `strcpy()`) determine where a source string **ends** by scanning forward until it hits the first `0x00` byte, they don't trust or even look at any separately-tracked length. So `strcat(buffer, padding)` copies only the **779** `A`s that come before that forced-in null terminator, then stops, the 780th byte never gets copied at all.
- Net effect: the overflow buffer that was supposed to land exactly on the return address lands **one byte short** of it instead, a single off-by-one in string handling silently shifts the entire exploit's alignment.
- **The tell that gave this away**: the debugger showed EIP holding `0x9010090c` instead of the expected `0x10090c83`, same four bytes, rotated by one position. A rotated/shifted version of an expected value in a register is characteristic of an offset miscalculation specifically, not a wrong return address (a wrong address would produce a *different* value entirely, not a shifted version of the right one).

**The fix:** bump the allocation to `781` (still writing a 780-byte block of `A`s followed by the same forced terminator at the new final position), so `strcat` now copies the full intended 780 `A`s before stopping.

**Where this comes from:** this specific bug is unique to this exploit's own C source (not a documented CVE detail), but the underlying lesson, C's null-terminated string functions copy based on where `0x00` appears, not based on any buffer-size variable you think is authoritative, is a general and recurring category of C bug (also the root cause of classic strcpy-based buffer overflows themselves, ironically the same mechanism the whole exploit is built on).

**Where to look in the response:** a debugger's register view (EIP/register pane in Immunity Debugger or similar) after a crash. A rotated-bytes EIP value versus the expected return address is the specific signal to watch for.

🔁 **Seen in:** [[Fixing Exploits#14.1.5. Changing the Overflow Buffer|Fixing Exploits, 14.1.5]].

#### Tags: #OffsetMisalignment #Malloc #Memset #NullTerminatedStrings #CommandBreakdowns

---

## SEH overwrite: why `pop pop ret` and a short jump, not a direct return-address overwrite

**Full buffer shape:**
```python
junk = b"A" * 217
nseh = pack("<L", 0x06eb9090)   # short jump, 6 bytes forward
seh  = pack("<L", 0x1001ae86)   # pop pop ret, inside SSLEAY32.DLL
shellcode = b"\x90" * 16 + <generated shellcode>
```

**Piece by piece:**
- A **SEH-based** overflow is a different mechanism from the classic direct-EIP-overwrite exploit ([[Fixing Exploits#14.1.4. Fixing the Exploit|14.1.4]]'s Sync Breeze case): instead of overwriting a function's return address directly, the overflow reaches far enough to corrupt the **Structured Exception Handler chain**, a linked list of exception-handling records that every Windows thread maintains on its own stack.
- Each SEH record has two 4-byte fields: a pointer to the **next** SEH record (`nSEH`), and a pointer to the actual **handler function** for this record (`SEH`). The overflow overwrites both.
- `seh` gets overwritten with the address of a `pop pop ret` instruction sequence (found here inside `SSLEAY32.DLL`, a non-ASLR module shipped with the vulnerable app). When the corrupted stack triggers an exception, Windows' own SEH dispatcher looks up and **calls** whatever address sits in the `SEH` field, that's `pop pop ret`, which pops two values off the stack (discarding them) then executes `ret`, which pops a third value and jumps to it. That third value, thanks to how the exception-dispatch stack frame is laid out at the moment of the crash, ends up being the address of the **`nSEH`** field itself, so `pop pop ret` effectively redirects execution back to `nSEH`.
- `nSEH` only has 4 bytes to work with, not enough room for real shellcode, so it holds a **short jump** instruction instead (`\xeb\x06\x90\x90`, "jump forward 6 bytes"), just enough to hop clean over the corrupted SEH bytes and land in the NOP sled that follows.
- Why the NOP sled still matters here exactly like the EIP-overwrite case: the short jump's landing point has a little slack, `\x90`s absorb any small imprecision so execution slides forward into the real shellcode regardless.
- **Why SEH instead of a direct EIP overwrite at all**: some overflows corrupt the SEH chain before ever reaching a usable direct return address, or the application catches and "handles" the crash via SEH before a direct-overwrite technique would ever get a chance to fire. SEH becomes the exploitable primitive when it's the *first* thing that reliably breaks.

**Where this comes from:** Corelan Team's "Exploit writing tutorial part 3: SEH Based Exploits" is the canonical deep-dive on this exact mechanism (verified live, linked in full in [[Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Module Exercise VM #3]]).

**Where to look in the response:** not response-based, this is debugger-observable only, watch the SEH chain view (Immunity Debugger's SEH chain window, or `!exchain` in WinDbg) at the moment of the crash to confirm the handler address is attacker-controlled.

🔁 **Seen in:** [[Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Fixing Exploits, Module Exercise VM #3]] (Easy Chat Server, CVE-2004-2466-class).

#### Tags: #SEHOverflow #PopPopRet #ShortJump #NOPSled #CommandBreakdowns

---

## A target crash right after an uncaught BOF payload is a good sign, not a failure

**The scenario:**
```
$ python3 exploit.py <target> <port>
[*] Sending evil buffer...
[+] Done!
# (no listener was running, nothing caught)

$ python3 exploit.py <target> <port>   # ran again to test
ConnectionRefusedError: [Errno 111] Connection refused
```

**Piece by piece:**
- The first run's own script output (`[+] Done!`) only confirms the packet was *sent* and the socket write didn't error, it says nothing about whether the overflow itself actually landed correctly on the target.
- No listener was running, so even a perfectly successful overflow (correct offset, correct SEH/return address, shellcode executes cleanly and dials back home) would have nothing to connect to, the reverse shell connection attempt fails silently on the target side with nothing visible to the attacker.
- The **second** run's `ConnectionRefusedError` is the real signal: the vulnerable service itself is no longer listening on its port at all. That only happens if the first payload actually **crashed the target process**, a crash is direct, unambiguous proof the overflow reached and corrupted the process's memory in a way the OS couldn't recover from, which is strong evidence the offset/return-address/SEH-chain values in the payload are basically correct, not proof the exploit is broken.
- **Why this is worth internalizing as a general heuristic:** a wrong offset or garbage return address more often produces either *no visible effect at all* (the overflow doesn't reach anything meaningful) or an immediate, different-looking crash signature, whereas *"it worked well enough to crash the app, right up until the point it should have handed control to shellcode"* specifically points at "correct overwrite path, lost this particular attempt to a sequencing mistake" rather than "wrong values."

**Where this comes from:** general BOF exploitation experience/discipline rather than a specific documented source, the practical rule ("start the listener first, leave it running, then fire the exploit, never the other order") is the actual fix and prevention.

**Where to look in the response:** a `ConnectionRefusedError` (or the target's service simply not responding to anything, including a plain `curl`) immediately after an exploit attempt with no listener running is the tell. Reset the target VM, confirm the service is back (`curl` it), get the listener up and **confirmed running** first, then retry.

🔁 **Seen in:** [[Fixing Exploits#Module Exercise VM #3: Unknown service, memory corruption|Fixing Exploits, Module Exercise VM #3]].

#### Tags: #BOFDebugging #ListenerOrdering #CrashAsSignal #CommandBreakdowns

---

## **Outstanding**
- [ ] A genuine from-scratch offset/bad-char/return-address discovery workflow (Immunity Debugger + `mona.py`, Metasploit's `pattern_create`/`pattern_offset`), once a box requires deriving these rather than reusing a public exploit's own already-researched values. See [[Fixing Exploits#14.3. Wrapping Up|14.3]]'s HackTricks link for where to start.
