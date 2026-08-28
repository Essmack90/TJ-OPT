---
tags: [oscp, port-scan, triage, runbook]
box_sources: [clamAV, Pelican, Payday]
---

# Port Scan — Results Triage

*You've got open ports. Now run a service scan on them and decide which threads to pull first.*

---

| Command                                                       | Evidence                       | Works when                        | Notes                                                                                                  | ✅ Go to                         | ❌ If nothing works            |
| ------------------------------------------------------------- | ------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------- | ----------------------------- |
| `nmap -sC -sV -p <ports> -oA nmap/${BoxName}_services $BoxIP` | Version banners, script output | Always — run after full port scan | Paste the port list from the full scan. `-sC` runs default scripts, `-sV` grabs versions. Both matter. | Pick a service stage note below | Try adding `-Pn` if it's slow |
| Read the service versions and searchsploit obvious ones       | `searchsploit sendmail 8.13`   | Version in banner is specific     | If nmap gives you a version number, searchsploit it before enumerating further.                        | [[Foothold - Public Exploit]]   | Keep enumerating              |

---

## Triage Decision Tree

Look at your open ports and ask in this order:

1. **SNMP (UDP 161)?** → Always hit this first if open, it dumps the whole system [[SNMP - Enumeration]]
2. **SMB (139/445)?** → Check for null sessions, shares, version → [[SMB - Null Session]]
3. **FTP (21)?** → Anonymous login? [[FTP - Anonymous]]
4. **HTTP/HTTPS (80/443/8080)?** → Web app track → [[HTTP - Initial Recon]]
5. **SMTP (25)?** → Banner version → searchsploit → [[Foothold - Public Exploit]]
6. **SSH (22)?** → Usually not directly exploitable early. Note the version, come back if you find creds.

---

## What to Note Down

For each port, record: service name, version, anything weird. Log to `~/boxes/$BoxName/notes.md`.

**clamAV example (what caught the flag):**

| Port | Service | Version | Action taken |
|------|---------|---------|--------------|
| 25 | SMTP | Sendmail 8.13.4 | searchsploit → EDB 4761 |
| 161/udp | SNMP | public community string | snmp-check → clamav-milter process found |
| 60000 | SSH | Same hostkeys as 22 | Noted as unusual, not pursued |

---

## Screenshot

> 📸 Screenshot: service scan output, take this, you'll reference version numbers later

---

**Module:** [[06. Information Gathering|Information Gathering]], [[13. Locating Public Exploits|Locating Public Exploits]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
