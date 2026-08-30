# Linux - Web Enum

**Step 5 of 50 · Linux**

*Find hidden paths, login pages, uploads, CMS clues, and readable files on the web server.*

## Run this

```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -t 40 -o $BoxDir/nmap/ferox.txt
nikto -h http://$BoxIP/
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/admin
curl -s http://$BoxIP/login
```

## Example output

```

200  GET  /login.php
301  GET  /admin  -> /admin/
200  GET  /robots.txt
...
```
## What did you get?

- [ ] A CMS is identified → **Go to Step 6 · [[Linux - CMS Check]]**
- [ ] A login page is found → **Test credentials, then go to Step 10 · [[Linux - Exploit Search]]**
- [ ] A file upload is found → **Go to the file-upload path in the web runbook**
- [ ] Interesting files are found → **Read and save them, then go to Step 17 · [[Linux - Credential Search]]**
- [ ] Nothing useful appears → **Go to Step 10 · [[Linux - Exploit Search]]**

## Notes

Run the web checks against the actual web port if it is not 80.

## Gotcha

> [!warning] 💡
> A 403 response still proves that a path exists. Record it instead of discarding it.
