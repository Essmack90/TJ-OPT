# Windows - Web Enum

**Step 23 of 50 · Windows**

*Find IIS paths, login pages, uploads, and version information.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x html,txt,php -t 30 -o $BoxDir/nmap/ferox.txt
nikto -h http://$BoxIP/
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/ | tee $BoxDir/loot/index.html
```

## Example output

```

200  GET  /
301  GET  /admin  -> /admin/
200  GET  /upload.aspx
...
```
## What did you get?

- [ ] A login page is found → **Run `curl -s http://$BoxIP/ | grep -iE 'user|login|admin'` to inspect the page source, then submit only documented default credentials once**
- [ ] An XML form is found in the app source → **Go to Step 24 · [[Windows - XXE]]**
- [ ] A file upload is found → **Submit the harmless test file from Step 9 · [[Linux - File Upload]] and record the returned upload path**
- [ ] The application changes by hostname or redirects to a named host → **Go to Step 5A · [[Web - Virtual Host Enumeration]]**
- [ ] Interesting content or a version is found → **Go to Step 26 · [[Windows - Exploit Search]]**
- [ ] Nothing useful appears → **Go to Step 25 · [[Windows - SMB Enum]]**

## Notes

Read the page source as well as the rendered page.

## Gotcha

> [!warning] 💡
> A 403 response still proves that the path exists.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows technique reference
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Netmon|Netmon]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
