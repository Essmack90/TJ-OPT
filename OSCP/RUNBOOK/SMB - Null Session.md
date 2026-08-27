---
tags: [oscp, smb, smb-null-session, runbook]
box_sources: [clamAV, Snookums, Bratarina]
---

# SMB — Null Session

*SMB is open. Try null session first — no creds, anonymous access. Often leaks shares, usernames, or files.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `smbclient -L //$BoxIP -N` | Share listing (ADMIN$, IPC$, custom shares) | SMB accessible, null auth not disabled | `-N` = no password. Look for non-default shares (not just ADMIN$, IPC$, SYSVOL, NETLOGON). Custom names are always worth poking. | Browse each interesting share | No shares or "NT_STATUS_ACCESS_DENIED" → [[SMB - Authenticated Enum]] |
| `smbclient //$BoxIP/<share> -N` | File listing inside the share | Null session works and share is accessible | `ls` to list, `get <file>` to download. Always download everything interesting before doing anything else — box may revert. | Read/loot the files | "NT_STATUS_ACCESS_DENIED" → share requires creds |
| `enum4linux -a $BoxIP` | User list, share list, OS info, password policy | Null session accessible | Broad sweep. Key sections: users (SID brute), shares (same as smbclient -L), OS. Noisy but thorough. | Usernames → [[SSH - Brute Force]] or [[Creds - Password Spray]] | Nothing useful → [[SMB - Authenticated Enum]] |

---

## What to look for in shares

- **Config files** — web app configs, DB connection strings, `.env` files
- **Backup files** — `passwd.bak`, `shadow.bak`, anything ending in `.bak` or `.old`
- **Credentials** — plaintext passwords, connection strings, private keys
- **User data** — anything under a username folder

---

## Bratarina Example: passwd.bak

```bash
smbclient -L //192.168.183.71 -N
# Found: backups share

smbclient //192.168.183.71/backups -N
# ls → passwd.bak
# get passwd.bak
```

`passwd.bak` revealed neil (uid 1000, /home/neil) and SMTP service accounts (_smtpd, _smtpq). Passwords were `x` (shadow only) — not directly useful. But confirmed the username neil and hinted at SMTP services being important.

---

## Module Links

[[06. Information Gathering#6.4.4. SMB Enumeration|SMB Enumeration]]
