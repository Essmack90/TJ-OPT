---
tags: [oscp, snmp, enumeration, runbook]
box_sources: [clamAV]
---

# SNMP — Enumeration

*SNMP with a default or guessable community string is one of the highest-value findings in a box. Process list, installed software, network config, users, it dumps the works.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `snmpwalk -c public -v1 $BoxIP > snmp-walk.txt` | Raw OID dump saved to file | UDP 161 open, community string `public` | Raw output is hard to read. Save it, but also run snmp-check for the readable version. | Run snmp-check next | Try `-v2c` instead of `-v1` |
| `snmp-check $BoxIP` | Human-readable: system info, processes, network, users | UDP 161 open, public community | The process list section is the key one. Look for: service names + full command-line arguments (flags, config paths). On clamAV this revealed `--black-hole-mode`. | [[Foothold - Public Exploit]] | Try other community strings: `private`, `manager`, `community` |
| `onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt $BoxIP` | Valid community strings listed | Public doesn't work | Brute-force community strings. Try this if `public` returns nothing. | Re-run snmp-check with found community string | SNMP not useful, move on |

---

## What to Look for in snmp-check Output

**Processes section** is the most useful part. Look for:
- Security software running (AV, WAF, milter), version and flags tell you if it's vulnerable
- Services you didn't see in nmap (running but not listening externally)
- Cron jobs or scripts in process list
- Any process with a config file path, that file might be readable/writable

**clamAV example — the line that cracked this box:**
```
3778  runnable  clamav-milter  /usr/local/sbin/clamav-milter  --black-hole-mode -l -o -q /var/run/clamav/clamav-milter.ctl
```
`--black-hole-mode` is the flag that enables the RCE. Without SNMP you'd never know it was there.

**Also check:**
- `[*] System information` — hostname, OS version, exact kernel
- `[*] Network information` — IPs, routing, sometimes internal subnets
- `[*] TCP connections` — services not visible from the outside

---

## Screenshot

> 📸 Screenshot: snmp-check process list output, especially any interesting service with full command line

---

**Module:** [[Information Gathering]]
