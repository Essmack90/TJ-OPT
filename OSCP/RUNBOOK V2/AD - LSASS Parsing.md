# AD - LSASS Parsing

**Step 44A of 50 · AD**

*Parse an acquired LSASS minidump offline, validate recovered credentials, and route usable NTLM material to the correct AD path.*

## When to use this page

Use this page when an authenticated SMB share or another authorized source provides an LSASS minidump. LSASS is the Windows process that holds logon authentication material. `pypykatz` parses the dump locally, so the target does not need a live credential-dumping tool.

## Parse the dump

> **Why:** `pypykatz` is an offline LSASS parser; it extracts authentication credentials from a memory dump on Kali. Save the output privately and look for account names, NT hashes, and validation clues.
```bash
pypykatz lsa minidump $BoxDir/loot/lsass.dmp | tee $BoxDir/loot/pypykatz.txt
```

> **Why:** This filter narrows the saved parser output to account and NT-hash lines so you can identify candidates without repeatedly displaying the entire dump.
```bash
grep -E 'NT:|Username:' $BoxDir/loot/pypykatz.txt | head -20
```

## Example output

```text
Username: $Username3
NT: [redacted]
```

## What did you get?

- [ ] A current service-account password is recovered → **Run `netexec smb $BoxIP -u $Username -p $Password`, store it privately, and go to Step 40 · [[AD - Credential Validation]]**
- [ ] An NT hash is recovered → **Set `$AdminHash` only for the intended privileged account, run `evil-winrm -i $BoxIP -u $Username -H $AdminHash`, then go to Step 49 · [[AD - Pass the Hash]]**
- [ ] Only a cached or stale account appears → **Run `netexec smb $BoxIP -u $Username -p $Password`, then go to Step 45 · [[AD - BloodHound]] if authentication fails**
- [ ] The parser fails → **Run `file $DumpFile` and confirm it reports a Windows minidump, then return to the authenticated share or collection stage**

## Notes

Parsing is offline and does not prove that a credential is still valid. Never place passwords or hashes in shared notes, screenshots, or command output sent to Claude.

## Gotcha

> [!warning] 💡
> A cached Administrator credential may be stale after a password change. Validate each account over the service you intend to use before treating the result as a foothold.

## Additional routing

- [ ] An NT hash belongs to a privileged account → **Validate it and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] The dump has no usable material → **Return to authenticated share triage and collect a different authorized dump**
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
