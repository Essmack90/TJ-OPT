# BloodHound-Python

Remote BloodHound data collection from Kali using only valid domain credentials. No binary needs to run on the target. Produces the same JSON files as SharpHound but works over LDAP and SMB from an external machine.

Cross-links: [[22. Active Directory Introduction and Enumeration|AD.7.1]], [[Active Directory Methodology#Step 7: BloodHound|AD Methodology Phase 1 Step 7]], [[Active Directory (Decision Tree)#I need to collect BloodHound data but can't run SharpHound on the target|Decision Tree]]

---

## What problem it solves

SharpHound.exe needs to run on a domain-joined Windows machine (or be executed via WinRM/RDP). When you have domain credentials but no Windows foothold yet (just Kali and a VPN to the DC), bloodhound-python collects the same data over the network. It's also useful when AV blocks SharpHound but LDAP queries from Kali are not monitored.

## Install

```bash
pip3 install bloodhound
# Or: git clone https://github.com/dirkjanm/BloodHound.py
```

## Usage

```bash
# Collect all BloodHound data types (-c all)
# -ns = nameserver (point at the DC for DNS resolution)
bloodhound-python -d INLANEFREIGHT.LOCAL -u forend -p Klmcargo2 \
  -ns 172.16.5.5 -c all
# Writes: computers.json, domains.json, groups.json, users.json, sessions.json

# Zip and import into BloodHound GUI
zip -r bh_data.zip *.json
# In BloodHound: Upload Data → select bh_data.zip
```

Specific collection methods (faster if you only need certain data):
```bash
-c DCOnly    # just DC info (fast, minimal traffic)
-c Group     # group memberships only
-c Session   # active sessions (requires SMB access to each host — slow)
-c Trusts    # domain trust relationships
```

## vs SharpHound

| Aspect | SharpHound.exe | bloodhound-python |
|---|---|---|
| Runs on | Domain-joined Windows host | Kali (Linux) |
| Session data | Yes (SMB-based) | Yes (but slower) |
| AV risk | High (EXE on target) | None (traffic looks like LDAP) |
| Speed | Fast | Moderate |
| Requires foothold | Yes (WinRM/RDP) | No (just domain creds) |

## Caveats

- Session collection (`-c Session`) makes SMB connections to each domain computer, noisy and slow on large domains. Use `-c DCOnly` or `-c Group,ObjectProps` if you just need the attack paths.
- Results may be slightly less complete than SharpHound because it can't collect certain local group membership data without actually logging in.
- Requires the DC to be reachable on LDAP (port 389) and optionally SMB (port 445) from Kali.
- `-ns` must point at the DC that resolves the domain; if DNS resolution fails, add the DC to `/etc/hosts`.

#### Tags: #ModernTooling #BloodHoundPython #BloodHound #RemoteCollection #ActiveDirectory #LDAP #HTBSupplementary
