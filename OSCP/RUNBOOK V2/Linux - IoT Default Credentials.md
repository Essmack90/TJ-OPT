# Linux - IoT Default Credentials

**Linux/Web branch · IoT product fingerprinting and controlled factory-credential validation**

*Use this stage when a web header, login page, hostname, or service banner identifies an appliance, Raspberry Pi image, router, media server, or other embedded product.*

## Why this stage exists

IoT software is often deployed from an image with a documented factory account. The assessment task is to identify the product first, validate one plausible credential against one appropriate service, and then move to local enumeration. This is controlled credential validation, not blind password spraying.

## Run this

> **Why:** These requests preserve the headers and page content that identify the product, version, login path, or firmware family.
```bash
curl -sS -i "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/http-root.txt"
curl -sS -L "http://$BoxIP:$WebPort/admin/" \
  | tee "$BoxDir/loot/http-admin.html"
grep -Ein 'product|version|firmware|login|admin|pi-hole|router|camera' \
  "$BoxDir/loot/http-root.txt" "$BoxDir/loot/http-admin.html"
```

> **Why:** This request checks for exposed repository metadata without assuming that the repository contains credentials. Save only the metadata needed to support the decision.
```bash
curl -sS "http://$BoxIP:$WebPort/admin/.git/HEAD" \
  | tee "$BoxDir/loot/application-git-head.txt"
```

## Example output

```text
X-Product: example-appliance
X-Version: 3.1.4
/admin/  (Status: 301)
X-Pi-hole: The Pi-hole Web interface is working!
```

Focus on the product name, version, and login path. A 404 or redirect can still be useful if the headers identify the application.

## Validate one appropriate service

Set the account name from the product or application evidence. Use a lab-approved factory credential privately at the prompt; do not put the value in shell history, a screenshot, or a shared note.

> **Why:** This tests the named account against SSH without placing a credential in the command line. Success is a shell whose identity matches the account under test.
```bash
ssh -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -p "$SshPort" "$Username@$BoxIP"
```

Immediately prove the identity:

```bash
id
whoami
hostname
```

## What did you get?

- [ ] Product and version are identified, but no account is known -> **Check the vendor's documented factory account in the authorised lab material, set `$Username`, and validate it against the product's own login or SSH once.**
- [ ] The default account succeeds over SSH -> **Save the login evidence privately and go to [[Linux - Local Enum]], then [[Linux - Sudo Check]].**
- [ ] The web login succeeds but SSH is closed -> **Use the web session only to enumerate configuration and user-management features; do not assume the web password is valid for SSH.**
- [ ] The credential fails once -> **Stop the default-credential branch and return to [[Linux - Credential Search]] or the product-specific service stage. Do not spray the value.**
- [ ] `.git/HEAD` or other metadata is exposed -> **Save the metadata and inspect only the relevant history/configuration; if it has no site-specific secret, return to service and credential triage.**

## Beginner focus

| Output clue | What it proves | Move next |
|---|---|---|
| Product header or footer | The web server belongs to a known appliance | Search the product's admin paths and version details |
| `/admin/` redirect or login form | A management surface exists | Save the page, identify version and field names |
| Factory account accepts authentication | The deployment kept its default credential | Run `id`, `hostname`, and local enumeration |
| `id` shows a service or appliance user | The SSH/web session identity is confirmed | Run [[Linux - Sudo Check]] and credential search |
| Credential fails | The hypothesis is not validated | Stop and choose a different evidence-based branch |

## Mounted removable media branch

If local enumeration shows a removable device or a read-only mount, record metadata before opening files. This distinguishes a forensic clue from an authorised content-recovery task.

> **Why:** These commands show the device, filesystem, mount mode, and directory metadata without printing file contents.
```bash
mount | grep -E '/media|/mnt|/dev/sd'
lsblk -f
df -h
ls -la "$UsbMount"
file -s "$UsbDevice"
stat "$UsbMount"/* 2>/dev/null
```

If the directory contains completion or flag material, do not run `cat`, `strings`, or a recursive content search in shared output. Record the path privately and continue to [[Linux - Clean Down]] unless the exercise explicitly requires forensic recovery.

## Gotchas

> [!warning] 💡
> Never put the candidate password in `ssh user:password@host`, process arguments, a command transcript, or a screenshot.

> [!warning] 💡
> A readable `.git/` directory is not automatically a foothold. Check whether it contains site-specific history before spending time on a vendor repository.

> [!warning] 💡
> Product login success and SSH success are separate facts. Record which service accepted the account and validate the identity after login.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- Pi-hole fingerprint, unchanged IoT credential validation over SSH, passwordless sudo, and safe mounted-USB metadata collection.

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Credential Search]]
- [[Linux - Local Enum]]
- [[Linux - Sudo Check]]
- [[Linux - Clean Down]]

## External resources

- [Pi-hole documentation](https://docs.pi-hole.net/)
- [CISA: Secure by Design](https://www.cisa.gov/securebydesign)
- [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things/)

## Why this matters for OSCP

This stage prevents a beginner from treating every old appliance as an exploit hunt. Fingerprint the product, validate one evidence-based credential, prove the session identity, and then let local enumeration choose the escalation path.
