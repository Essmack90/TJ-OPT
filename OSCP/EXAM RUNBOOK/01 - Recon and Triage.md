# Recon and Triage

Run the fast scanner first, then confirm the result with Nmap. The output needed for the next decision is the complete open-port list, service product, version, hostname, and any domain or web clue.

## Fast loop

### Run this

~~~bash
rustscan -a "$BoxIP" --ulimit 5000 -- -Pn -n -sC -sV -oA "$BoxDir/nmap/rustscan"
OpenPorts="$(awk '$1 ~ /^[0-9]+\/tcp$/ && $2 == "open" {sub("/tcp", "", $1); ports=ports (ports ? "," : "") $1} END {print ports}' "$BoxDir/nmap/rustscan.nmap" 2>/dev/null)"
if [ -z "$OpenPorts" ]; then
  sudo nmap -Pn -n -sS -p- --min-rate 5000 "$BoxIP" -oA "$BoxDir/nmap/allports"
  OpenPorts="$(awk '$1 ~ /^[0-9]+\/tcp$/ && $2 == "open" {sub("/tcp", "", $1); ports=ports (ports ? "," : "") $1} END {print ports}' "$BoxDir/nmap/allports.nmap" 2>/dev/null)"
fi
boxset OpenPorts "$OpenPorts"
sudo nmap -Pn -n -sC -sV -p "$OpenPorts" "$BoxIP" -oA "$BoxDir/nmap/services"
sudo nmap -Pn -n -sU --top-ports 100 "$BoxIP" -oA "$BoxDir/nmap/udp-top100"
~~~

### Example output

~~~text
22/tcp  open  ssh
80/tcp  open  http
445/tcp open  microsoft-ds
~~~

### What did you get?

- [ ] HTTP or HTTPS -> **Open [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]].**
- [ ] SSH or Linux services -> **Open [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path|Linux Fast Path]].**
- [ ] SMB, RPC, RDP, or WinRM without the AD set -> **Open [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]].**
- [ ] Kerberos, LDAP, Global Catalog, or supplied domain credentials -> **Open [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]].**
- [ ] UDP 500 or 4500 is IKE/IPSec -> **Open [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport|IKE-IPSec Transport]], then repeat the TCP scan.**
- [ ] FTP, DNS, SNMP, or an unusual application port -> **Run the matching row in [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]].**
- [ ] No usable port list -> **Read the saved scan, correct `$OpenPorts`, and rerun the targeted scan.**

### Open next

Use the selected branch above. Preserve the full scan before starting application or exploit work.

## 1. Fast discovery

~~~bash
rustscan -a "$BoxIP" --ulimit 5000 -- -Pn -n -sC -sV -oA "$BoxDir/nmap/rustscan"
~~~

If RustScan is absent or incomplete, use the full Nmap fallback:

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 "$BoxIP" -oA "$BoxDir/nmap/allports"
~~~

Extract the comma-separated open-port list from the saved scan, then confirm versions:

~~~bash
OpenPorts="$(awk '$1 ~ /^[0-9]+\/tcp$/ && $2 == "open" {sub("/tcp", "", $1); ports=ports (ports ? "," : "") $1} END {print ports}' "$BoxDir/nmap/allports.nmap" 2>/dev/null)"
if [ -z "$OpenPorts" ]; then
  OpenPorts="$(awk '$1 ~ /^[0-9]+\/tcp$/ && $2 == "open" {sub("/tcp", "", $1); ports=ports (ports ? "," : "") $1} END {print ports}' "$BoxDir/nmap/rustscan.nmap" 2>/dev/null)"
fi
boxset OpenPorts "$OpenPorts"
sudo nmap -Pn -n -sC -sV -p "$OpenPorts" "$BoxIP" -oA "$BoxDir/nmap/services"
sudo nmap -Pn -n -sU --top-ports 100 "$BoxIP" -oA "$BoxDir/nmap/udp-top100"
~~~

## 2. Port-to-branch triage

| Output clue | Fast action |
| --- | --- |
| 80, 443, 8000, 8080, 8088, 8888, or another HTTP port | Set `$WebPort`; open [[OSCP/EXAM RUNBOOK/02 - Web and Services\|Web and Services]]. |
| 21/tcp | Test anonymous FTP, then inspect files and web-root upload paths. |
| 22/tcp | Keep SSH for credential validation; do not brute force before evidence. |
| 135, 139, 445, 3389, or 5985 | Open [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path\|Windows Fast Path]]; if domain clues exist, use [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]]. |
| 53/tcp or 53/udp | Test DNS version, recursion, and AXFR when a hostname is known. |
| 88, 389, 636, 3268, or 3269 | Open [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]]. |
| 161/udp | Run SNMP community checks and route disclosed values to the correct service. |
| 500/udp or 4500/udp | Open [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport\|Windows - IKE-IPSec Transport]] and inspect UDP 161 or TCP services after the gate. |
| 25565 or another application port | Fingerprint it and keep it correlated with the web service; do not discard it as background noise. |

## 3. Immediate evidence checks

~~~bash
awk '$2 == "open" {print FILENAME ":" $0}' "$BoxDir/nmap/services.nmap" "$BoxDir/nmap/udp-top100.nmap" 2>/dev/null
grep -Ei 'domain|realm|hostname|server|product|version|wordpress|apache|iis|smb|ldap|kerberos' \
  "$BoxDir/nmap"/* 2>/dev/null | tee "$BoxDir/loot/triage-clues.txt"
~~~

## Branches

- **Open TCP ports, no useful versions:** run targeted Nmap scripts for the identified service, then use [[OSCP/EXAM RUNBOOK/06 - Modern Tooling|Modern Tooling]].
- **Only UDP services are visible:** confirm the route and run the service-specific UDP stage before changing VPN settings.
- **A service is slow or times out:** compare a known static request and a saved Nmap result before declaring a network failure.
- **The box description names a CVE:** do not use it until product, version, path, and access condition match the scan.

## Detailed routes

- [[OSCP/RUNBOOK V2/Port Triage|RUNBOOK V2 Port Triage]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows Service Scan]]
- [[OSCP/RUNBOOK V2/AD - Service Scan|AD Service Scan]]
- [[OSCP/MODULES/06. Information Gathering|Module 6 - Information Gathering]]
