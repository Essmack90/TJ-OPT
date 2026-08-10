# NetExec (nxc)

The actively-maintained successor to CrackMapExec (now inactive). A single tool for authenticating against and enumerating SMB/WinRM/MSSQL/LDAP/RDP/SSH/VNC/FTP across one host or an entire subnet at once.

---

## What it replaces, and why it's faster

[[Information Gathering#6.4.4. SMB Enumeration|6.4.4]] teaches `enum4linux`, `nbtscan`, and `smbclient -L` one host at a time, each tool doing one narrow job. NetExec rolls host OS/version fingerprinting, share enumeration, null-session checking, and (once you have creds) command execution into one consistent syntax that also just works against a whole subnet instead of a single IP, genuinely useful once a network has more than one box worth checking, not just a one-host convenience.

## Install

```bash
sudo apt install netexec
```

## Usage

```bash
# Unauthenticated fingerprint + null-session check, single host or a whole subnet
netexec smb <target>
netexec smb 192.168.1.0/24

# Enumerate shares once you have creds
netexec smb <target> -u <user> -p <pass> --shares

# Blank/anonymous creds explicitly
netexec smb <target> -u '' -p ''

# Execute a command once you have admin-equivalent creds (needs valid admin access, this isn't a vuln-finder)
netexec smb <target> -u <user> -p <pass> -x 'whoami'
```
*Same underlying auth mechanics as `smbclient`/`enum4linux`, NetExec is a convenience/consistency wrapper, not a different attack. Genuinely useful once you're spraying the same creds across many hosts, which manual `smbclient` doesn't do at all.*

## Where this applies in the vault

- [[Information Gathering#6.4.4. SMB Enumeration|6.4.4, SMB Enumeration]], as a faster/broader alternative to `enum4linux`/`nbtscan` for the same recon goal
- [[Windows Methodology#Step 2: SMB Enumeration|Windows Methodology, Step 2]]
- Already used ad hoc in the Active box writeup for credential verification, this entry formalizes it as a general recon-speed tool rather than a one-off

#### Tags: #ModernTooling #NetExec #CrackMapExec #SMB #ActiveDirectory
