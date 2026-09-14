# AD - Credential Validation

**Step 40 of 50 · AD**

*Check a recovered credential against the services that can provide the next step.*

## Run this

> **Why:** This authenticated SMB or WinRM check validates the recovered credential and reveals whether the account has the requested access.
```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
```

## Example output

```

SMB  10.10.10.1  445  DC01  [+] htb.local\username:password
WINRM 10.10.10.1  5985 DC01  [+] Pwn3d!
LDAP 10.10.10.1  389  DC01  [+] Authenticated
```
## What did you get?

- [ ] WinRM authentication succeeds → **Go to Step 41 · [[AD - WinRM Foothold]]**
- [ ] LDAP authentication succeeds → **Go to Step 45 · [[AD - BloodHound]]**
- [ ] SMB authentication succeeds only → **Check shares and go to Step 42 · [[AD - Group Triage]]**
- [ ] All services reject the credential → **Run `date -u`, recheck `$Username`, `$Password`, and `$Domain`, then go to Step 35 · [[AD - Clock Sync]]**

## Notes

Use `$Username` and `$Password` rather than putting private credentials into notes.

### Kerberos-first validation when NTLM is disabled

When a password-based check returns `STATUS_NOT_SUPPORTED`, obtain a TGT and validate the cache with the target FQDN:

```bash
KRB5_CONFIG=$BoxDir/notes/krb5.conf \
KRB5CCNAME=$BoxDir/loot/$Username.ccache \
  nxc smb $FQDN -d $Domain -k --use-kcache --kdcHost $BoxIP
```

The `[+] ... from ccache` line proves that the credential and Kerberos configuration work. A client can still fail independently if its WinRM module is NTLM-only; switch to a Kerberos-aware Evil-WinRM or Impacket client rather than discarding the valid ticket.

## Gotcha

> [!warning] 💡
> Test the exact domain context. A valid local account or wrong domain can produce a misleading authentication failure.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- validated the recovered service and administrator accounts over SMB
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- validated Cameron over SMB and WinRM on COLTY
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- validated the Winlogon-recovered account against DC01 SMB/WinRM and later confirmed Administrator pass-the-hash
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- validated `P.Rosa`, `C.Neri`, and recovered admin caches while NTLM was disabled

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Search evidence

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- validated Hope over LDAP/SMB, web_svc after cracking, Edgar after spraying, and Sierra before retrieving the certificate backup.
