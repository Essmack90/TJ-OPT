---
tags: [OffSec, Challenge, Multi-machine, AD, Windows, Linux, DA]
platform: OffSec Challenge
os: Multi-OS (Ubuntu, Win10, Windows Server)
hostname: Challenge1
difficulty: Challenge
ip: 192.168.147.141
status: Complete
domain: oscp.exam
---

# Challenge1 (OffSec) — Kill Chain

## Scope & objectives

Capture all 7 flags: .143, .144 (Linux), MS01, MS02 (Windows/AD members), DC01 (domain controller), and .145 (Win10 workgroup). Achieved Domain Admin via password-reused tom_admin NT hash from MS02's stale windows.old SAM.

## Key findings

- `.144` (Ubuntu 22.04): exposed `.git/` (leaked PAT + site backups); recovered `joomla:Password@1` (MySQL) + `stuart:BreakingBad92` (SSH) from history/backups. Root via CVE-2023-0386 (OverlayFS/FUSE).
- `.143` (Ubuntu 20.04): web/app services → root (previously ROOTED).
- `MS01`: WAMP + Attendance & Payroll → local admin hash used via PtH.
- `MS02`: `celia.almeda` (low-priv domain user) could read `C:\windows.old\Windows\System32\config\{SAM,SYSTEM}` → old local `tom_admin` NT hash (`4979d69d4ca66955c075c41cf45f24dc`) matched domain `tom_admin` (RID 1108, Domain Admins) due to password reuse.
- `DC01`: PtH with reused tom_admin hash; secretsdump (DCSync), got krbtgt + Administrator NT; proof.txt.
- `.145` (Win10 Pro workgroup): WiFi Mouse/MouseServer RCE (CVE-2022-3218) on tcp/1978 (openfile → utf8 with double-CR) as `offsec`. PuTTY saved session in HKCU revealed plaintext password for `zachary` (local admin). Remote admin blocked by UAC remote token filtering → used local scheduled task (`schtasks /ru /rp`) to run with full token → proof.txt.

## Techniques

- Leaked `.git` → commit history/PAT + backup artefacts.
- Windows stale-hive credential reuse (`windows.old` SAM/SYSTEM).
- Registry saved-session credential hunting (PuTTY) → cleartext password.
- UAC remote token filtering → local scheduled task bypass.
- WiFi Mouse MouseServer RCE (CVE-2022-3218).
- CVE-2023-0386 OverlayFS (Linux kernel 5.15).
- Pass-the-Hash; DCSync (post-DA).

## Evidence

- `loot/` (flags, creds, DCSync NTDS/kerberos, MS02 windows.old hives, LSA, winPEAS)
- `nmap/*.txt` (service + all-port scans)
- `logs/` (preserved session captures + shell outputs)
- `Challenge1-engagement.log` (reconstructed transcript, ingested into log memory)

## Outcome

All 7 flags captured. DA achieved. Evidence preserved; target-side staged tooling removed.
