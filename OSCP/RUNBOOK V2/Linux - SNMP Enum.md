# Linux - SNMP Enum

**Step 4 of 50 · Linux**

*Check whether SNMP is exposed on UDP 161 and walk it for usernames, processes, and credentials.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
sudo nmap -sU --top-ports 100 $BoxIP -oN $BoxDir/nmap/udp.txt
snmpwalk -c public -v1 $BoxIP
snmp-check $BoxIP
```

## Example output

UDP scan showing SNMP open:

```
161/udp  open  snmp
```

snmp-check pulling users and processes:

```
[*] Users accounts:
  root
  username
[*] Running processes:
  sendmail
  apache
[*] Software components:
  ...
```

## What did you get?

- [ ] UDP 161 is open → **Run snmpwalk and snmp-check and save the full output to `$BoxDir/loot/snmp.txt`**
- [ ] Usernames appear in the output → **Save them to `$BoxDir/loot/users.txt` and go to Step 10 · [[Linux - Exploit Search]] or the AS-REP path if AD**
- [ ] Running process names reveal the stack (sendmail, apache, etc.) → **Cross-reference with Step 10 · [[Linux - Exploit Search]]**
- [ ] Credentials appear in the walk output → **Validate them and go to Step 17 · [[Linux - Credential Search]]**
- [ ] Community string `public` returns nothing → **Try `private` and `manager`; if still empty, SNMP is locked down**
- [ ] UDP 161 is closed → **Go to Step 5 · [[Linux - Web Enum]]**

## Notes

SNMP community string `public` is the default and works on a large proportion of OSCP boxes. Always run a UDP scan in parallel with the TCP service scan — SNMP is easy to miss.

`snmp-check` formats the walk output into labelled sections (users, processes, installed software, network interfaces) and is easier to skim than raw `snmpwalk`.

## Gotcha

> [!warning] 💡
> UDP scans are slow and unreliable without `sudo`. Always run with `sudo nmap -sU`. A closed UDP port and a filtered UDP port look similar — open ports are unambiguous.

## External Resources

| Resource | Link |
|---|---|
| HackTricks — SNMP | https://book.hacktricks.xyz/network-services-pentesting/pentesting-snmp |
| PayloadsAllTheThings — SNMP | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Network%20Discovery.md |
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
