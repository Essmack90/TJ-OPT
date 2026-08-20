---
tags: [oscp, port-scan, runbook]
box_sources: [clamAV]
---

# Port Scan — Full

*Run this at the start of every box. Goal: find all open TCP ports, then hand off to [[Port Scan - Results Triage]].*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP` | Open port list in terminal | Always — run this first | Fast full TCP scan. `-oA` saves all three formats. Check `nmap/${BoxName}_allports.nmap` afterwards. | [[Port Scan - Results Triage]] | Try `--min-rate 5000` if timing out |
| `nmap -sU --top-ports 100 $BoxIP` | `161/udp open snmp` etc. | After TCP scan — run in parallel or after | UDP is slow. Top 100 covers SNMP (161), DNS (53), TFTP (69), NTP (123). Don't skip it. | [[SNMP - Enumeration]] if 161 is open | Increase to `--top-ports 200` |
| `nmap -sU -p 161 $BoxIP` | `161/udp open snmp` | Targeted SNMP check when you suspect it | Faster than full UDP if you're specifically checking for SNMP | [[SNMP - Enumeration]] | Move on |

---

## Screenshot

> 📸 Screenshot: full port scan output in terminal, take this before moving on

---

## Notes

- Always save output with `-oA nmap/${BoxName}_allports`, you'll come back to the .nmap file
- Port 60000 on clamAV was SSH, same hostkeys as port 22, unusual, not the attack path
- If the target filters (all ports `filtered`), try `-Pn` to skip host discovery

---

**Module:** [[Information Gathering]]
